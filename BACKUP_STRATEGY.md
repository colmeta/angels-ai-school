# 💾 Backup & Disaster Recovery Strategy

**Angels AI School Management Platform**

---

## 🎯 Backup Strategy

### Automated Daily Backups

**Database (Supabase):**
- **Frequency:** Every 24 hours at 2 AM UTC
- **Retention:** 30 days rolling
- **Location:** Supabase automatic backups
- **Verification:** Automated restore test weekly

**File Storage (User Uploads):**
- **Frequency:** Real-time sync to S3
- **Retention:** 90 days
- **Location:** AWS S3 (multi-region)
-**Verification:** Integrity check daily

---

## 📋 Backup Types

### 1. Full Backup (Daily)
- Complete database snapshot
- All user-uploaded files
- Configuration files
- Logs (last 7 days)

**Size:** ~5GB per school (estimate)  
**Time:** ~15 minutes

### 2. Incremental Backup (Every 6 hours)
- Changed data only
- Transaction logs
- New uploads

**Size:** ~500MB per increment  
**Time:** ~2 minutes

### 3. Point-in-Time Recovery
- Restore to any moment in last 7 days
- Transaction log replay
- Granular recovery

---

## 🔄 Recovery Procedures

### Scenario 1: Accidental Data Deletion
**Recovery Time Objective (RTO):** < 1 hour  
**Recovery Point Objective (RPO):** < 15 minutes

**Steps:**
1. Identify deleted data timestamp
2. Access Supabase dashboard
3. Navigate to Backups → Point-in-Time
4. Select timestamp before deletion
5. Restore specific tables
6. Verify data integrity

### Scenario 2: Complete Database Loss
**RTO:** < 4 hours  
**RPO:** < 24 hours

**Steps:**
1. Create new Supabase project
2. Download latest daily backup
3. Restore schema from `database/COMPLETE_DATABASE_SCHEMA.sql`
4. Import data from backup
5. Run migrations (if needed)
6. Update DATABASE_URL in environment
7. Restart services
8. Verify all schools accessible

### Scenario 3: Regional Outage
**RTO:** < 2 hours  
**RPO:** Real-time (S3 multi-region)

**Steps:**
1. DNS failover to backup region (automatic)
2. Verify database replication status
3. Point traffic to standby instance
4. Monitor performance
5. Communicate with users

---

## 🧪 Testing Schedule

| Test Type | Frequency | Last Tested |
|-----------|-----------|-------------|
| Restore Test (Single Table) | Weekly | [TBD] |
| Full Database Restore | Monthly | [TBD] |
| Disaster Recovery Drill | Quarterly | [TBD] |
| Multi-Region Failover | Yearly | [TBD] |

---

## 📊 Backup Monitoring

**Automated Alerts:**
- ❌ Backup failed
- ⚠️ Backup size anomaly (>200% variation)
- ⚠️ Restoration test failed
- ⚠️ Storage approaching limit

**Alert Channels:**
- Email: admin@angels-ai.com
- SMS: +256 700 000 000
- Slack: #backup-alerts

---

## 🗂️ Manual Backup (Emergency)

### Database Export
```bash
# Via Supabase CLI
supabase db dump -f backup.sql

# Via pg_dump
PGPASSWORD=your_password pg_dump \
  -h your-host.supabase.co \
  -U postgres \
  -d postgres \
  > backup-$(date +%Y%m%d).sql
```

### File Export
```bash
# Sync uploads to local
aws s3 sync s3://angels-ai-uploads ./backups/uploads/

# Create tar archive
tar -czf backup-files-$(date +%Y%m%d).tar.gz ./backups/uploads/
```

---

## 🔐 Backup Security

### Encryption
- **At Rest:** AES-256 encryption
- **In Transit:** TLS 1.3
- **Keys:** AWS KMS managed

### Access Control
- **Backup Access:** Admin only
- **Restore Access:** Admin + Senior Engineer
- **Audit:** All access logged

### Compliance
- GDPR compliant (30-day retention for deleted schools)
- Data residency: EU/US/Africa regions available
- Right to erasure: Backup purge within 30 days

---

## 💰 Backup Costs (Estimate)

| Component | Monthly Cost |
|-----------|--------------|
| Supabase Backups | Included (Pro plan) |
| S3 Storage (500GB) | $12/month |
| S3 Replication | $5/month |
| Backup Monitoring (Sentry) | $0 (free tier) |
| **TOTAL** | **~$17/month** |

Scales with usage (~$0.03/GB/month)

---

## 📞 Disaster Recovery Contacts

**Primary:** CTO - +256 700 000 000  
**Secondary:** DevOps Lead - +256 700 000 001  
**Vendor Support:** Supabase - support@supabase.io

---

## ✅ Checklist for New Schools

When onboarding a new school:
- [ ] Verify automatic backup enabled
- [ ] Test restore for first backup
- [ ] Configure backup notifications
- [ ] Document custom requirements
- [ ] Schedule first DR drill

---

**Last Updated:** December 18, 2025  
**Next Review:** March 18, 2026
