from datetime import datetime

from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django.db.models import Sum, F
from django.db import transaction as db_transaction

from billing.api.serializers import BillingTransactionSerializer
from billing.models import BillingAccount
from billing.models import BillingTransaction as Transaction


def send_email_notification(worker: str, descr: str, amount: float):
    """
    mocking the sending of email notifications
    """
    print(f"sending email notification to {str(worker)[:6]} with msg `{descr} ${amount}`")
    # FIXME: implement email sending


def send_payment_slips_to_bank(slips: list):
    """
    mocking the sending of payment slips to the bank
    """
    print(f"sent {len(slips)} to the bank")
    # FIXME: implement sending to the bank


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = BillingTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["post"], url_path="cashout", permission_classes=[permissions.IsAdminUser])
    def cash_out(self, request):
        t = Transaction.objects.prefetch_related("account").all()

        agg = t.values("account", "account__user__public_id").annotate(Sum("debit"), Sum("credit"))

        pmnts_list = []
        for row in agg:
            worker_balance = row["debit__sum"] - row["credit__sum"]
            if worker_balance > 0:
                worker_public_id = str(row["account__user__public_id"])
                print(f"dry run: would cash out {worker_balance} to user {str(worker_public_id)[:6]}")

                # TODO probably could be done via bulk_create() but it doesn't call save() on the model
                with db_transaction.atomic():
                    pmnt = Transaction(
                        billing_cycle_id=datetime.date(datetime.today()),
                        account=BillingAccount.objects.get(pk=row["account"]),
                        description=f"make payment according to current balance",
                        type=Transaction.TransactionType.PAYMENT,
                        credit=worker_balance,
                    )
                    pmnt.save()

                    BillingAccount.objects.filter(user__public_id=worker_public_id).update(balance=F("balance") - worker_balance)

                send_email_notification(worker_public_id, "daily cashout, popug!", worker_balance)
                pmnts_list.append((worker_public_id, worker_balance))

        if pmnts_list:
            send_payment_slips_to_bank(pmnts_list)

            return Response(
                {p[0]:p[1] for p in pmnts_list},
                status=status.HTTP_200_OK,
            )

        return Response(
            {'status': 'no workers with positive balance found — nothing to cashout'},
            status=status.HTTP_204_NO_CONTENT,
        )
