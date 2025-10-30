# ⚡ Quick Fix Guide - HTTP 500 Error

**Problem**: HTTP 500 Internal Server Error when accessing `https://prismod.co.ke/app/sigma`

**Root Cause**: MariaDB database service is not running (killed due to out-of-memory)

**Fix Time**: ~2-5 minutes

---

## 🔧 Quick Fix Steps

### Step 1: Restart MariaDB (1 minute)

```bash
# SSH into the server
ssh frappe@prismod.co.ke

# Navigate to frappe-bench
cd /home/frappe/frappe-bench

# Restart MariaDB
sudo systemctl restart mariadb

# Verify it's running
sudo systemctl status mariadb
```

**Expected Output**:
```
● mariadb.service - MariaDB 10.6.22 database server
     Loaded: loaded (/lib/systemd/system/mariadb.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2025-10-28 09:00:00 UTC; 5s ago
```

---

### Step 2: Restart Frappe Services (1 minute)

```bash
# Restart all Frappe services
bench restart

# Or restart specific site
bench --site prismod.co.ke restart
```

---

### Step 3: Clear Cache (30 seconds)

```bash
# Clear Frappe cache
bench --site prismod.co.ke clear-cache
```

---

### Step 4: Verify Fix (1 minute)

```bash
# Test the application
curl -I https://prismod.co.ke/app/sigma/

# Should return HTTP 200 or 302 (not 500)
```

**Expected Output**:
```
HTTP/2 302
location: https://prismod.co.ke/app/sigma/
```

---

## ✅ Verification

### In Browser

1. Open: `https://prismod.co.ke/app/sigma/`
2. Should redirect to login or dashboard
3. No 500 error
4. Page loads normally

### In Terminal

```bash
# Check logs for errors
tail -20 logs/web.error.log

# Should show no recent errors
```

---

## 🚨 If Problem Persists

### Check MariaDB Status

```bash
# Check if MariaDB is actually running
ps aux | grep mariadb

# Check MariaDB logs
sudo tail -50 /var/log/mysql/mariadb.log

# Try to connect to database
mysql -u frappe -p -e "SELECT 1;"
```

### Check Memory

```bash
# Check available memory
free -h

# Check disk space
df -h

# If low on memory, restart the server
sudo reboot
```

### Check Frappe Logs

```bash
# View error logs
tail -100 logs/web.error.log

# View access logs
tail -100 logs/web.log

# View system logs
sudo journalctl -u mariadb -n 100
```

---

## 📊 Monitoring

### Monitor Memory Usage

```bash
# Real-time memory monitoring
watch -n 1 free -h

# Or use top
top -b -n 1 | head -20
```

### Monitor MariaDB

```bash
# Check MariaDB status
sudo systemctl status mariadb

# Check MariaDB processes
ps aux | grep mariadb

# Check MariaDB connections
mysql -u root -p -e "SHOW PROCESSLIST;"
```

---

## 🔍 Root Cause

**Why did MariaDB crash?**

MariaDB was killed due to **Out-Of-Memory (OOM)** condition at 08:44:26 UTC.

**Possible causes**:
- Memory leak in database
- Large queries consuming too much memory
- Insufficient server RAM
- Too many database connections

**Solution**:
- Restart MariaDB (temporary fix)
- Monitor memory usage (ongoing)
- Optimize queries (long-term)
- Increase server RAM (if needed)

---

## 📋 Checklist

- [ ] SSH into server
- [ ] Restart MariaDB: `sudo systemctl restart mariadb`
- [ ] Verify MariaDB running: `sudo systemctl status mariadb`
- [ ] Restart Frappe: `bench restart`
- [ ] Clear cache: `bench --site prismod.co.ke clear-cache`
- [ ] Test application: `curl -I https://prismod.co.ke/app/sigma/`
- [ ] Verify no 500 error
- [ ] Check logs: `tail -20 logs/web.error.log`

---

## 📞 Support

If the issue persists:

1. Check `ERROR_INVESTIGATION_REPORT.md` for detailed analysis
2. Review logs in `logs/web.error.log`
3. Contact system administrator
4. Check server resources: `free -h`, `df -h`

---

**Status**: ✅ QUICK FIX PROVIDED
**Time to Fix**: ~2-5 minutes
**Difficulty**: Easy

