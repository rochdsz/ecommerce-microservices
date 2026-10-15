                        [ Client / Browser / UI ]
                                    │
                                    ▼
                         [ NGINX API Gateway ]
                               (Port 80)
      ┌──────────────┬──────────────┼──────────────┬──────────────┐
      │              │              │              │              │
 /api/v1/auth   /api/v1/prod   /api/v1/inv    /api/v1/orders  /api/v1/pay
      │              │              │              │              │
      ▼              ▼              ▼              ▼              ▼
[User Service] [Product Svc]  [Inventory Svc] [Order Service] [Payment Svc]
  (Port 8001)    (Port 8002)    (Port 8003)    (Port 8004)    (Port 8005)
      │              │              │           │      │          │
      ▼              ▼              ▼           │      │          ▼
 [users_db]    [products_db]  [inventory_db]    │      │    [payments_db]
                                                ▼      ▼
                                       REST to Inv    REST to Pay