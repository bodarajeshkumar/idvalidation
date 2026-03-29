# OpenShift Deployment Guide

This guide provides instructions for deploying the Data Retrieval System to OpenShift.

## 📋 Prerequisites

- OpenShift CLI (`oc`) installed
- Access to an OpenShift cluster
- Docker or Podman (for local testing)
- IBM Cloudant credentials

## 🚀 Quick Deployment

### 1. Login to OpenShift

```bash
oc login <your-openshift-cluster-url>
```

### 2. Update Secrets

Edit [`secrets.yaml`](secrets.yaml) and replace the placeholder values with your actual credentials:

```yaml
stringData:
  api-base-url: "https://your-instance.cloudant.com/database/_design/view/_view/name"
  api-key: "your-api-key"
  api-password: "your-api-password"
```

### 3. Run Deployment Script

```bash
cd openshift
./deploy.sh
```

The script will:
- Create/switch to the project
- Create secrets and persistent volumes
- Build Docker images
- Deploy backend and frontend
- Create routes
- Display access URLs

## 📁 File Structure

```
openshift/
├── backend.Dockerfile           # Backend container image
├── frontend.Dockerfile          # Frontend container image
├── nginx.conf                   # Nginx configuration for frontend
├── backend-deployment.yaml      # Backend deployment config
├── frontend-deployment.yaml     # Frontend deployment config
├── services.yaml                # Service definitions
├── routes.yaml                  # Route definitions
├── secrets.yaml                 # Secret template (update before deploying)
├── persistent-volumes.yaml      # PVC definitions
├── deploy.sh                    # Automated deployment script
└── README.md                    # This file
```

## 🔧 Manual Deployment

If you prefer to deploy manually:

### Step 1: Create Project

```bash
oc new-project data-retrieval
```

### Step 2: Create Secrets

```bash
# Update secrets.yaml first, then:
oc apply -f secrets.yaml
```

### Step 3: Note on Storage

This deployment uses `emptyDir` volumes for storage (data stored within pods). Data will be lost if pods are deleted or restarted. For production use, consider configuring PersistentVolumeClaims.

### Step 4: Build Images

```bash
# Backend
oc new-build --name=backend --binary --strategy=docker
oc start-build backend --from-dir=.. --follow

# Frontend
oc new-build --name=frontend --binary --strategy=docker
oc start-build frontend --from-dir=.. --follow
```

### Step 5: Deploy Services

```bash
oc apply -f services.yaml
```

### Step 6: Deploy Applications

```bash
# Update YOUR_PROJECT in deployment files first
oc apply -f backend-deployment.yaml
oc apply -f frontend-deployment.yaml
```

### Step 7: Create Routes

```bash
oc apply -f routes.yaml
```

## 🔍 Verification

### Check Pod Status

```bash
oc get pods
```

Expected output:
```
NAME                        READY   STATUS    RESTARTS   AGE
backend-xxxxxxxxxx-xxxxx    1/1     Running   0          2m
frontend-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
```

### Check Services

```bash
oc get svc
```

### Check Routes

```bash
oc get routes
```

### View Logs

```bash
# Backend logs
oc logs -f deployment/backend

# Frontend logs
oc logs -f deployment/frontend
```

## 🌐 Accessing the Application

After deployment, get the route URLs:

```bash
# Frontend URL
oc get route frontend-route -o jsonpath='{.spec.host}'

# Backend URL
oc get route backend-route -o jsonpath='{.spec.host}'
```

Access the application at: `https://<frontend-route-url>`

## ⚙️ Configuration

### Environment Variables

Backend environment variables are configured in [`backend-deployment.yaml`](backend-deployment.yaml):
- `API_BASE_URL` - Cloudant API endpoint
- `API_KEY` - Cloudant API key
- `API_PASSWORD` - Cloudant password

### Resource Limits

Default resource allocations:

**Backend:**
- Requests: 512Mi memory, 250m CPU
- Limits: 2Gi memory, 1000m CPU

**Frontend:**
- Requests: 128Mi memory, 100m CPU
- Limits: 512Mi memory, 500m CPU

Adjust in deployment YAML files as needed.

### Storage

**Current Configuration:**
- Uses `emptyDir` volumes (ephemeral storage within pods)
- Output data stored at `/app/output`
- Checkpoint data stored at `/app/checkpoint`
- **Note:** Data is lost when pods are deleted or restarted

**For Production:**
To use persistent storage, replace `emptyDir` with PersistentVolumeClaims in [`backend-deployment.yaml`](backend-deployment.yaml):

```yaml
volumes:
- name: output-data
  persistentVolumeClaim:
    claimName: output-data-pvc
- name: checkpoint-data
  persistentVolumeClaim:
    claimName: checkpoint-data-pvc
```

Then create PVCs using [`persistent-volumes.yaml`](persistent-volumes.yaml)

## 📊 Scaling

### Scale Backend

```bash
oc scale deployment/backend --replicas=2
```

### Scale Frontend

```bash
oc scale deployment/frontend --replicas=3
```

### Auto-scaling

Create a Horizontal Pod Autoscaler:

```bash
oc autoscale deployment/backend --min=1 --max=5 --cpu-percent=80
oc autoscale deployment/frontend --min=2 --max=10 --cpu-percent=70
```

## 🔒 Security

### Secrets Management

- Never commit actual credentials to version control
- Use OpenShift secrets for sensitive data
- Rotate credentials regularly

### Network Policies

Consider adding network policies to restrict traffic:

```bash
oc apply -f network-policies.yaml  # Create this file as needed
```

### RBAC

Ensure proper role-based access control:

```bash
oc adm policy add-role-to-user view <username> -n data-retrieval
```

## 🐛 Troubleshooting

### Pods Not Starting

```bash
# Check pod events
oc describe pod <pod-name>

# Check logs
oc logs <pod-name>
```

### Image Pull Errors

```bash
# Check build status
oc get builds

# View build logs
oc logs build/<build-name>
```

### Connection Issues

```bash
# Test backend connectivity
oc rsh deployment/frontend
curl http://backend-service:5001/api/health

# Test from outside
curl https://<backend-route>/api/health
```

### Storage Issues

**Note:** Current deployment uses `emptyDir` volumes. Data is ephemeral and will be lost on pod restart.

To check volume mounts:
```bash
# Check volume mounts in pod
oc describe pod <pod-name>

# Access pod and check directories
oc rsh <pod-name>
ls -la /app/output
ls -la /app/checkpoint
```

## 🔄 Updates and Rollbacks

### Update Application

```bash
# Rebuild and deploy
oc start-build backend --from-dir=.. --follow
oc rollout restart deployment/backend

# Or use the deploy script
./deploy.sh
```

### Rollback Deployment

```bash
# View rollout history
oc rollout history deployment/backend

# Rollback to previous version
oc rollout undo deployment/backend

# Rollback to specific revision
oc rollout undo deployment/backend --to-revision=2
```

## 🧹 Cleanup

### Delete All Resources

```bash
oc delete project data-retrieval
```

### Delete Specific Resources

```bash
oc delete -f backend-deployment.yaml
oc delete -f frontend-deployment.yaml
oc delete -f services.yaml
oc delete -f routes.yaml
oc delete -f persistent-volumes.yaml
oc delete -f secrets.yaml
```

## 📈 Monitoring

### View Resource Usage

```bash
# Pod metrics
oc adm top pods

# Node metrics
oc adm top nodes
```

### Set Up Monitoring

OpenShift includes built-in monitoring. Access the console:

```bash
oc get routes -n openshift-console
```

Navigate to: **Monitoring → Dashboards**

## 🔗 Additional Resources

- [OpenShift Documentation](https://docs.openshift.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Project README](../README.md)
- [Full Stack Setup Guide](../docs/FULL_STACK_SETUP.md)

## 💡 Tips

1. **Use Labels**: All resources are labeled with `app: data-retrieval` for easy filtering
2. **Health Checks**: Both deployments include liveness and readiness probes
3. **Persistent Storage**: Data persists across pod restarts
4. **TLS Enabled**: Routes use edge TLS termination by default
5. **Non-root Containers**: All containers run as non-root for security

## 📞 Support

For issues or questions:
1. Check pod logs: `oc logs -f deployment/<name>`
2. Review events: `oc get events --sort-by='.lastTimestamp'`
3. Consult OpenShift documentation
4. Review project documentation in `docs/` directory

---

**Last Updated:** 2026-03-29