mkdir -p /var/run/secrets/kubernetes.io/serviceaccount/
kubectl config view --raw -o jsonpath='{.clusters[0].cluster.certificate-authority-data}' | base64 -d > ls 
echo "your-service-account-token" > /var/run/secrets/kubernetes.io/serviceaccount/token


