# OWASP API Risk Recognition

A. GET /orders/{id} returns any order without checking ownership
   → Broken Object Level Authorization

B. Admin endpoint has no role check
   → Broken Function Level Authorization

C. API accepts unlimited expensive export requests
   → Unrestricted Resource Consumption

D. Deprecated /v1 endpoint remains exposed and undocumented
   → Improper Inventory Management
