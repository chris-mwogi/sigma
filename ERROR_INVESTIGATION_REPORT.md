# 🔍 HTTP 500 Error Investigation Report

**Date**: 2025-10-28
**Status**: ✅ ROOT CAUSE IDENTIFIED
**Severity**: CRITICAL - Database Service Down

---

## 🚨 Root Cause Analysis

### Primary Issue: MariaDB Service Killed (OOM)

**Error**: `pymysql.err.OperationalError: (2003, "Can't connect to MySQL server on '127.0.0.1' ([Errno 111] Connection refused")`

**Root Cause**: MariaDB was killed due to **Out-Of-Memory (OOM)** condition

**Evidence from logs**:
```
× mariadb.service - MariaDB 10.6.22 database server
     Active: failed (Result: oom-kill) since Tue 2025-10-28 08:44:26 UTC
   Main PID: 1024 (code=killed, signal=KILL)
```

---

## 📊 Error Details

### Stack Trace Analysis

The error occurs in this sequence:

1. **Request arrives** at `/app/sigma`
2. **Frappe tries to handle exception** in `frappe/app.py:324`
3. **Frappe calls** `get_system_settings()` to check error traceback setting
4. **Database connection attempted** to fetch System Settings
5. **Connection fails** - MariaDB is not running
6. **HTTP 500 returned** to client

### Full Error Chain

```
gunicorn worker → Frappe app → Exception handler → get_system_settings()
→ get_cached_doc() → get_doc() → get_controller() → import_controller()
→ frappe.db.get_value() → database.sql() → database.connect()
→ mariadb.get_connection() → pymysql.connect()
→ ❌ Connection refused (MariaDB not running)
```

---

## 🔧 Solution

### Step 1: Restart MariaDB Service

```bash
# Check current status
sudo systemctl status mariadb

# Restart the service
sudo systemctl restart mariadb

# Verify it's running
sudo systemctl status mariadb
```

### Step 2: Verify Database Connection

```bash
# Test MySQL connection
mysql -u root -p -e "SELECT 1;"

# Or for Frappe user
mysql -u frappe -p -e "SELECT 1;"
```

### Step 3: Restart Frappe Services

```bash
cd /home/frappe/frappe-bench
bench restart
```

### Step 4: Clear Cache

```bash
bench --site prismod.co.ke clear-cache
```

### Step 5: Test Application

```bash
# Access the application
curl -I https://prismod.co.ke/app/sigma/

# Should return HTTP 200 (or 302 redirect if not logged in)
```

---

## 📋 Verification Checklist

- [ ] MariaDB service is running: `sudo systemctl status mariadb`
- [ ] Database is accessible: `mysql -u frappe -p -e "SELECT 1;"`
- [ ] Frappe services restarted: `bench restart`
- [ ] Cache cleared: `bench --site prismod.co.ke clear-cache`
- [ ] Application loads: `https://prismod.co.ke/app/sigma/`
- [ ] No 500 errors in logs: `tail -f logs/web.error.log`

---

## 🔍 Why MariaDB Ran Out of Memory

### Possible Causes

1. **Memory Leak** - Long-running queries or connections
2. **Large Dataset** - Excessive data in memory
3. **Insufficient RAM** - Server doesn't have enough memory
4. **Unoptimized Queries** - Inefficient database queries
5. **Connection Pool Exhaustion** - Too many open connections

### Recommendations

1. **Monitor Memory Usage**
   ```bash
   free -h
   top -b -n 1 | head -20
   ```

2. **Check MariaDB Configuration**
   ```bash
   cat /etc/mysql/mariadb.conf.d/50-server.cnf | grep -E "max_connections|innodb_buffer_pool_size"
   ```

3. **Review Slow Queries**
   ```bash
   tail -100 /var/log/mysql/mariadb.log | grep "Query_time"
   ```

4. **Optimize Database**
   ```bash
   bench --site prismod.co.ke console
   frappe.db.commit()
   ```

---

## 🚀 Prevention Measures

### 1. Monitor Memory

```bash
# Add to crontab for hourly monitoring
0 * * * * free -h >> /var/log/memory_usage.log
```

### 2. Set Memory Limits

Edit `/etc/mysql/mariadb.conf.d/50-server.cnf`:

```ini
# Limit memory usage
max_connections = 100
innodb_buffer_pool_size = 1G
```

### 3. Enable Swap

```bash
# Check swap
free -h

# If no swap, create it
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 4. Set Up Alerts

```bash
# Monitor disk and memory
sudo apt-get install sysstat
sar -r 1 10  # Memory usage every 1 second for 10 times
```

---

## 📝 Logs to Check

### MariaDB Logs
```bash
tail -100 /var/log/mysql/mariadb.log
```

### Frappe Logs
```bash
tail -100 logs/web.error.log
tail -100 logs/web.log
```

### System Logs
```bash
sudo journalctl -u mariadb -n 50
sudo dmesg | tail -20
```

---

## ✅ Status After Fix

Once MariaDB is restarted:

- ✅ Database connection restored
- ✅ Frappe can fetch System Settings
- ✅ Application routes work
- ✅ Frontend assets load
- ✅ API calls succeed
- ✅ HTTP 500 errors resolved

---

## 📞 Support

If the issue persists after restarting MariaDB:

1. Check available disk space: `df -h`
2. Check available memory: `free -h`
3. Review MariaDB error log: `tail -100 /var/log/mysql/mariadb.log`
4. Check Frappe logs: `tail -100 logs/web.error.log`
5. Contact system administrator

---

## 🎯 Next Steps

1. **Immediate**: Restart MariaDB service
2. **Short-term**: Verify application works
3. **Medium-term**: Monitor memory usage
4. **Long-term**: Optimize database and queries

---

**Report Generated**: 2025-10-28
**Investigated By**: Augment Agent
**Status**: ✅ ROOT CAUSE IDENTIFIED - SOLUTION PROVIDED

