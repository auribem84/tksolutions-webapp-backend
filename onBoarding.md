# 🚀 Onboarding & Multi-Tenant Setup

This document describes how the application initializes its **multi-tenant architecture**, including the creation of a **default organization**, **admin user**, and rules for onboarding new organizations and users.

---

## 🧩 Overview

The system is built using a **multi-tenant model**, where:

* Each user belongs to an **organization**
* Access and data are scoped per organization
* A special **default organization** acts as the system owner

---

## 🏁 Application Startup (Automatic Seeding)

When the application starts, it automatically runs a database seed process.

### ✅ What gets created:

1. **Default Organization**

   * ID: `DEFAULT_ORG_ID`
   * Name: `TKDefaultOrg`
   * Acts as the **root/system organization**

2. **Roles**

   * `admin`
   * `member`

3. **Default Admin User**

   * Email: defined by `DEFAULT_ADMIN_EMAIL`
   * Password: defined in seed (should be changed in production)
   * Assigned **admin role**

4. **Organization Link**

   * The admin user is linked to the default organization
   * Has `admin` role within it

---

## 🔐 Default Organization Rules

The **default organization** is special and has elevated privileges:

### ✔ Only users in the default org can:

* Create new organizations
* Bootstrap new tenants

### ❌ Regular organizations cannot:

* Create other organizations
* Access data outside their own organization

---

## 🏢 Organization Creation (Bootstrap Flow)

A new organization can only be created via the **bootstrap endpoint**.

### 🔒 Access Control

* Requires authentication
* User **must belong to the default organization**
* User must have **admin role**

---

### 📌 Bootstrap Process

When creating a new organization:

1. A new **organization** is created
2. A new **admin user** is created
3. The user is assigned:

   * The new organization
   * The `admin` role

---

## 👥 User Management Rules

### Within each organization:

* Admins can:

  * Create users
  * Assign roles (if implemented)
  * Manage their organization

* Users:

  * Are scoped strictly to their organization
  * Cannot access other organizations

---

## ⚠️ Important Constraints

* Every user **must belong to an organization**
* No cross-organization access is allowed
* JWT tokens include:

  * `user_id`
  * `organization_id`
  * `role_id`

---

## 🔄 Example Flow

### First Run

```
App starts → seed runs → default org + admin created
```

---

### Creating a New Organization

```
Default Admin logs in
→ Calls /organizations/bootstrap
→ New org + admin user created
```

---

### Managing Users in New Org

```
Org Admin logs in
→ Creates users within their org only
```

---

## 🔐 Security Notes

* Change default admin credentials in production
* Protect bootstrap endpoint strictly
* Always validate `organization_id` in queries

---

## ✅ Summary

| Feature       | Behavior                         |
| ------------- | -------------------------------- |
| Default Org   | Created automatically at startup |
| Org Creation  | Only by default org admin        |
| User Scope    | Limited to their organization    |
| Multi-Tenancy | Strict isolation enforced        |

---

## 🚀 Future Improvements

* Role-based permissions (RBAC)
* Organization quotas (limit users/resources)
* Audit logging per organization
* Invitation-based onboarding

---

This setup ensures a **secure, scalable, and production-ready multi-tenant foundation**.
