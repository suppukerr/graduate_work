import json

YOOKASSA_WEBHOOK_SUCCESS = json.loads("""
{
  "type": "notification",
  "event": "payment.succeeded",
  "object": {
    "id": "3086206f-000f-5000-8000-1e653030dc24",
    "status": "succeeded",
    "amount": {
      "value": "1.00",
      "currency": "RUB"
    },
    "income_amount": {
      "value": "0.96",
      "currency": "RUB"
    },
    "description": "string",
    "recipient": {
      "account_id": "1183493",
      "gateway_id": "2557458"
    },
    "payment_method": {
      "type": "bank_card",
      "id": "3086206f-000f-5000-8000-1e653030dc24",
      "saved": false,
      "status": "inactive",
      "title": "Bank card *4477",
      "card": {
        "first6": "555555",
        "last4": "4477",
        "expiry_year": "2025",
        "expiry_month": "12",
        "card_type": "MasterCard",
        "card_product": {
          "code": "E"
        },
        "issuer_country": "US"
      }
    },
    "captured_at": "2025-10-18T21:55:24.823Z",
    "created_at": "2025-10-18T21:54:55.346Z",
    "test": true,
    "refunded_amount": {
      "value": "0.00",
      "currency": "RUB"
    },
    "paid": true,
    "refundable": true,
    "metadata": {
      "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "cms_name": "yookassa_sdk_python",
      "user_subscription_id": "6dc41f73-177a-49b9-b8cb-946f8fb1314b"
    },
    "authorization_details": {
      "rrn": "869559887526342",
      "auth_code": "910915",
      "three_d_secure": {
        "applied": true,
        "protocol": "v1",
        "method_completed": false,
        "challenge_completed": true
      }
    }
  }
}
""")

YOOKASSA_WEBHOOK_FAILED = json.loads("""
{
  "type": "notification",
  "event": "payment.canceled",
  "object": {
    "id": "3085f72f-000f-5000-8000-1156fcfc6c92",
    "status": "canceled",
    "amount": {
      "value": "1.00",
      "currency": "RUB"
    },
    "description": "string",
    "recipient": {
      "account_id": "1183493",
      "gateway_id": "2557458"
    },
    "payment_method": {
      "type": "bank_card",
      "id": "3085f72f-000f-5000-8000-1156fcfc6c92",
      "saved": false,
      "status": "inactive"
    },
    "created_at": "2025-10-18T18:58:55.544Z",
    "test": true,
    "paid": false,
    "refundable": false,
    "metadata": {
      "user_id": "00000000-0000-0000-0000-000000000000",
      "cms_name": "yookassa_sdk_python",
      "user_subscription_id": "6dc41f73-177a-49b9-b8cb-946f8fb1314b"
    },
    "cancellation_details": {
      "party": "yoo_money",
      "reason": "expired_on_confirmation"
    }
  }
}
""")
