# D-Lab Workshop Catalog Maintenance Guide

This document provides step-by-step procedures for maintaining the D-Lab workshop catalog website. It's designed to be used by maintainers to keep dependencies updated, troubleshoot issues, and ensure the site continues to run smoothly.

## 🗓️ Quarterly Maintenance Tasks

### Python Dependency Updates

**When**: Every 3 months or when security advisories are published

**Steps**:
1. Check for outdated packages:
   ```bash
   pip list --outdated
   ```

2. Review current pinned versions in `requirements.txt`:
   - `google-auth`
   - `google-auth-oauthlib` 
   - `google-auth-httplib2`
   - `google-api-python-client`
   - `PyYAML`

3. Update to latest stable versions:
   ```bash
   pip install --upgrade google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client PyYAML
   pip freeze | grep -E "(google-|PyYAML)" > temp_versions.txt
   ```

4. Update `requirements.txt` with new pinned versions

5. Test locally:
   ```bash
   pip install -r requirements.txt
   python scripts/fetch_workshop_catalog.py  # Test Google Sheets connection
   python scripts/fetch_google_sheets.py     # Test workshop data fetch
   ```

6. Commit and push changes, monitor CI workflow

### Ruby Dependency Updates

**When**: Every 3 months or when security advisories are published

**Steps**:
1. Check for outdated gems:
   ```bash
   bundle outdated
   ```

2. Update Gemfile.lock:
   ```bash
   bundle update
   ```

3. Test locally:
   ```bash
   bundle exec jekyll serve --host 127.0.0.1 --port 4001
   ```

4. Verify site builds correctly and all pages load

5. Commit updated `Gemfile.lock`

## 🚨 Security Update Procedures

### When Security Vulnerabilities Are Reported

1. **Check GitHub Security Advisories** in repository settings
2. **Review Dependabot alerts** if enabled
3. **Update affected packages immediately**:
   - For Python: Update version in `requirements.txt`
   - For Ruby: Run `bundle update [gem-name]`
4. **Test thoroughly** before deploying
5. **Deploy ASAP** after testing

## 🔧 Troubleshooting Common Issues

### Google Sheets API Failures

**Symptoms**: Nightly workflow fails with authentication errors

**Diagnosis**:
```bash
# Check if service account key is valid
python -c "
import json
import os
key = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY')
if key:
    parsed = json.loads(key)
    print(f'Service account: {parsed.get(\"client_email\")}')
    print(f'Project: {parsed.get(\"project_id\")}')
else:
    print('GOOGLE_SERVICE_ACCOUNT_KEY not set')
"
```

**Solutions**:
- Verify Google Service Account key hasn't expired
- Check Google Sheets API quota limits
- Ensure sheets are accessible to service account

### Jekyll Build Failures

**Symptoms**: Site doesn't build or missing content

**Common Causes & Solutions**:
1. **Ruby version mismatch**:
   ```bash
   # Check current Ruby version
   ruby --version
   # Should match .ruby-version (3.2)
   ```

2. **Missing gems**:
   ```bash
   bundle install
   ```

3. **Liquid template errors**:
   - Check `_includes/` files for syntax errors
   - Validate YAML front matter in pages

### Workflow Failures

**Check workflow logs**:
1. Go to GitHub Actions tab
2. Click on failed workflow run
3. Expand failed step to see error details

**Common fixes**:
- Re-run failed jobs (often transient API issues)
- Check if Google Sheets are accessible
- Verify all required secrets are set in repository settings

## 📊 Monitoring and Health Checks

### Daily Checks
- [ ] Nightly workflow completed successfully
- [ ] Website loads correctly at https://dlab-berkeley.github.io/dlab-workshops/
- [ ] Workshop data appears current

### Weekly Checks
- [ ] Review workflow logs for any warnings
- [ ] Spot-check a few workshop pages for correct data
- [ ] Verify upcoming workshops are displaying

### Monthly Checks
- [ ] Review GitHub Actions usage (should be <500 minutes/month)
- [ ] Check for any security advisories
- [ ] Verify Google Sheets integration is working

## 🔄 GitHub Actions Workflows

### `nightly-update.yml`
**Purpose**: Updates workshop data and rebuilds site daily
**Schedule**: 12:30 AM PST (7:30 AM UTC)
**Triggers**: Schedule + manual

**Manual trigger**:
1. Go to Actions tab
2. Select "Nightly Workshop Data Update and Site Rebuild"
3. Click "Run workflow"

### `jekyll.yml`
**Purpose**: Builds and deploys Jekyll site
**Triggers**: Push to main branch + manual

## 📝 Version Pinning Strategy

### Why We Pin Versions
- **Prevent silent breakages** from upstream API changes
- **Ensure reproducible builds** across environments
- **Control update timing** rather than surprise breakages

### What We Pin
- **Python packages**: All Google API clients and dependencies
- **Ruby version**: Fixed at 3.2 via `.ruby-version`
- **Ruby gems**: Via `Gemfile.lock` (auto-generated)

### Update Schedule
- **Quarterly**: Routine dependency updates
- **As needed**: Security patches
- **Major versions**: Planned upgrades with testing

## 🆘 Emergency Procedures

### Site Down or Broken
1. **Check GitHub Pages status**: https://www.githubstatus.com/
2. **Roll back recent changes**:
   ```bash
   git revert [commit-hash]
   git push
   ```
3. **Manual site rebuild**:
   - Go to Actions → "Build and deploy Jekyll site"
   - Click "Run workflow"

### Data Not Updating
1. **Check Google Sheets access**: Verify sheets are accessible
2. **Manual workflow run**: Trigger nightly-update.yml manually
3. **Check service account permissions**: Ensure sheets are shared with service account

## 📚 Additional Resources

- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Ruby Version Management](https://github.com/rbenv/rbenv)

---

**Last Updated**: $(date '+%Y-%m-%d')
**Maintainer**: Tom v Nuenen

## Website handoff and recovery — 29 October 2026

Technical owner after Tom: **TBD**. These notes supersede the older runtime/maintainer details above.

- Site: https://dlab-berkeley.github.io/dlab-workshops/
- Nightly workflow: https://github.com/dlab-berkeley/dlab-workshops/actions/workflows/nightly-update.yml
- Catalog source: https://docs.google.com/spreadsheets/d/1YrUknesHuNO1FnckHa6VexmomDoCxP6RXwOaF_DtvVs/edit
- Upcoming-session source: https://docs.google.com/spreadsheets/d/18ZDs00wB67STWRband7CTraIfDDfaDwLQ-PoNP0LQzY/edit
- Runtime: nightly runner pinned to Ubuntu 24.04 with Python 3.9; upgrade Python and its pinned packages together before moving to a newer runner. Workflows use Ruby 3.4; .ruby-version specifies 3.4.1.
- Required repository secrets: GOOGLE_WORKSHOPS_SHEET_ID, GOOGLE_SHEET_ID, GOOGLE_SERVICE_ACCOUNT_KEY. Never print or commit the key.
- Current blocker: the shared drive explicitly blocks dlab-workshop-reader@dlab-admin.iam.gserviceaccount.com as a non-member/outside UC Berkeley. A shared-drive manager or campus administrator must approve an allowed access method before nightly imports can resume.
- Import failures now stop the workflow and preserve stored data. A valid schedule with no upcoming sessions can still publish an empty list. Run regression checks with: python -m unittest discover -s tests -v
- After access is restored, manually run the nightly workflow and inspect both fetch logs, data/upcoming_workshops.json (last_updated and total_workshops), and registration links on the live site. A green badge alone was insufficient with the old scripts.
- For manual recovery, an authorized maintainer can read the production Sheets and regenerate _data/workshops.yml and both upcoming_workshops.json files, then run scripts/generate_workshop_pages.py and build Jekyll before publishing. The 29 October snapshot contains six upcoming workshop listings.
- The incoming maintainer should disable/re-enable the scheduled workflow or edit its cron using their own GitHub account to take over scheduled-run alerts. Tom has set this repository to Ignore.
