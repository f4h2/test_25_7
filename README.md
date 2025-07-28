Tôi hiểu rằng bạn muốn làm sạch tài nguyên Kubernetes trên **Minikube** (thay vì Kind như trong hướng dẫn trước) để giải phóng tài nguyên trên máy local, và bạn cũng cần các lệnh để chạy lại ứng dụng Kubernetes khi cần. Dưới đây, tôi sẽ cung cấp các lệnh để hủy toàn bộ tài nguyên Minikube và các tài nguyên liên quan, đồng thời hướng dẫn cách chạy lại ứng dụng Flask trên cụm Minikube, dựa trên cấu hình đã mô tả trong hướng dẫn trước (ứng dụng Flask, Docker Hub, ConfigMap, Secret, Ingress, Health Checks, và tùy chọn PostgreSQL).

---

### 🧹 Hủy toàn bộ tài nguyên Kubernetes trên Minikube

Các bước dưới đây sẽ xóa cụm Minikube, các tài nguyên Kubernetes (Deployment, Service, Ingress, v.v.), và làm sạch các container/image Docker liên quan để giải phóng tài nguyên máy.

1. **Xóa cụm Minikube**:
   ```bash
   minikube delete
   ```
   - **Giải thích**: Xóa cụm Minikube hiện tại (bao gồm tất cả Pod, Service, Ingress, ConfigMap, Secret, v.v.) và các container liên quan. Nếu bạn có nhiều profile Minikube, chỉ định profile:
     ```bash
     minikube delete --profile myapp-cluster
     ```

2. **Kiểm tra xem cụm đã xóa chưa**:
   ```bash
   minikube status
   ```
   - **Giải thích**: Nếu cụm đã bị xóa, lệnh này sẽ báo rằng không tìm thấy cụm. Nếu cụm vẫn tồn tại, lặp lại bước 1.

3. **Xóa các container Docker liên quan (tùy chọn)**:
   - Kiểm tra các container đang chạy:
     ```bash
     docker ps -a
     ```
   - Xóa các container liên quan đến Minikube:
     ```bash
     docker rm -f $(docker ps -a -q --filter "name=minikube")
     ```
   - **Giải thích**: Loại bỏ các container Docker liên quan đến Minikube (thường có tên chứa "minikube").

4. **Xóa Docker image (tùy chọn)**:
   - Kiểm tra các image Docker:
     ```bash
     docker images
     ```
   - Xóa image của ứng dụng Flask (nếu không cần nữa):
     ```bash
     docker rmi <your_dockerhub_username>/myapp:latest
     ```
   - Xóa các image Minikube:
     ```bash
     docker rmi $(docker images -q gcr.io/k8s-minikube/*)
     ```
   - **Giải thích**: Giải phóng dung lượng bằng cách xóa image của ứng dụng và image Minikube.

5. **Xóa file cấu hình Kubernetes (tùy chọn)**:
   - Nếu bạn muốn xóa các file YAML trong thư mục `k8s/` để làm sạch hoàn toàn:
     ```bash
     rm -rf myapp/k8s/*
     ```
   - **Giải thích**: Xóa các file cấu hình Kubernetes trong thư mục dự án để tránh nhầm lẫn khi triển khai lại.

6. **Xóa Helm release và repository (nếu sử dụng Helm)**:
   - Gỡ cài đặt Helm release:
     ```bash
     helm uninstall myapp --namespace default
     helm uninstall my-postgres --namespace default
     helm uninstall monitoring --namespace monitoring
     ```
   - Xóa Helm repository cache:
     ```bash
     helm repo remove bitnami prometheus-community
     ```
   - Xóa thư mục Helm Chart (nếu không cần nữa):
     ```bash
     rm -rf myapp-chart
     ```
   - **Giải thích**: Loại bỏ các tài nguyên Helm và cache để làm sạch môi trường.

7. **Làm sạch Docker để giải phóng dung lượng (tùy chọn)**:
   - Xóa các container, image, và volume không sử dụng:
     ```bash
     docker system prune -a --volumes
     ```
   - **Lưu ý**: Cẩn thận với lệnh này vì nó sẽ xóa tất cả image và container không được sử dụng. Chỉ chạy nếu bạn chắc chắn không cần các image/container khác.

**Kết quả**:
- Cụm Minikube và các tài nguyên Kubernetes sẽ bị xóa.
- Máy local sẽ được giải phóng dung lượng và tài nguyên.

---

### 🚀 Chạy lại ứng dụng Kubernetes trên Minikube

Để chạy lại ứng dụng Flask trên cụm Minikube, bạn cần tái tạo cụm, cài đặt các phụ thuộc (như NGINX Ingress Controller, Metrics Server, Helm), và triển khai lại các tài nguyên Kubernetes. Dưới đây là các lệnh, giả định mã nguồn và file cấu hình vẫn được giữ nguyên trong thư mục `myapp/`.

1. **Tạo lại cụm Minikube**:
   ```bash
   minikube start --driver=docker
   ```
   - **Giải thích**: Tạo cụm Minikube mới sử dụng driver Docker (có thể thay bằng `virtualbox`, `hyperkit`, hoặc driver khác tùy hệ điều hành).
   - **Tùy chọn**: Chỉ định profile nếu cần:
     ```bash
     minikube start --driver=docker --profile myapp-cluster
     ```

2. **Kích hoạt addon Ingress trong Minikube**:
   ```bash
   minikube addons enable ingress
   ```
   - **Giải thích**: Kích hoạt NGINX Ingress Controller tích hợp sẵn trong Minikube để hỗ trợ Ingress.

3. **Cài đặt Metrics Server (cho HPA, nếu sử dụng)**:
   ```bash
   kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
   ```
   - **Giải thích**: Cung cấp metrics CPU để Horizontal Pod Autoscaler hoạt động.
   - **Tùy chọn**: Nếu Metrics Server gặp lỗi (do Minikube), thêm tham số `--kubelet-insecure-tls`:
     ```bash
     kubectl patch deployment metrics-server -n kube-system --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'
     ```

4. **Cài đặt Helm (nếu sử dụng Helm Chart)**:
   - Thêm lại Helm repository:
     ```bash
     helm repo add bitnami https://charts.bitnami.com/bitnami
     helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
     helm repo update
     ```

5. **Đẩy lại Docker image (nếu đã xóa)**:
   - Build và đẩy image:
     ```bash
     docker build -t <your_dockerhub_username>/myapp:latest ./myapp
     docker login -u <your_dockerhub_username> -p <your_dockerhub_password>
     docker push <your_dockerhub_username>/myapp:latest
     ```
   - **Giải thích**: Đảm bảo image ứng dụng Flask có sẵn trên Docker Hub.
   - **Tùy chọn với Minikube**: Nếu không muốn dùng Docker Hub, bạn có thể sử dụng registry của Minikube:
     ```bash
     eval $(minikube docker-env)
     docker build -t myapp:latest ./myapp
     ```
     - **Lưu ý**: Nếu dùng cách này, cập nhật `image` trong `k8s/deployment.yaml` thành `myapp:latest` thay vì `<your_dockerhub_username>/myapp:latest`, và bỏ `imagePullSecrets`.

6. **Triển khai lại tài nguyên Kubernetes (nếu không dùng Helm)**:
   ```bash
   kubectl create secret docker-registry dockerhub-secret \
     --docker-username=<your_dockerhub_username> \
     --docker-password=<your_dockerhub_password> \
     --docker-email=<your-email>
   kubectl apply -f myapp/k8s/configmap.yaml
   kubectl apply -f myapp/k8s/secret.yaml
   kubectl apply -f myapp/k8s/deployment.yaml
   kubectl apply -f myapp/k8s/service.yaml
   kubectl apply -f myapp/k8s/ingress.yaml
   kubectl apply -f myapp/k8s/hpa.yaml
   kubectl apply -f myapp/k8s/servicemonitor.yaml
   kubectl apply -f myapp/k8s/networkpolicy.yaml
   ```
   - **Giải thích**: Áp dụng các file YAML để triển khai ConfigMap, Secret, Deployment, Service, Ingress, HPA, ServiceMonitor, và NetworkPolicy.
   - **Lưu ý**: Nếu không dùng Docker Hub, bỏ dòng `imagePullSecrets` trong `k8s/deployment.yaml`.

7. **Triển khai PostgreSQL (nếu sử dụng)**:
   ```bash
   helm install my-postgres bitnami/postgresql --set auth.database=mydb --set auth.username=myuser --set auth.password=mypassword
   kubectl apply -f myapp/k8s/postgres-secret.yaml
   ```
   - **Giải thích**: Cài lại PostgreSQL và Secret để ứng dụng Flask kết nối cơ sở dữ liệu.

8. **Cài Prometheus/Grafana (nếu sử dụng)**:
   ```bash
   helm install monitoring prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace
   ```
   - **Giải thích**: Cài lại stack giám sát Prometheus/Grafana.
   - **Truy cập Grafana**:
     ```bash
     kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80
     ```
     - Truy cập: `http://localhost:3000` (mặc định: admin/prom-operator).

9. **Cấu hình truy cập Ingress**:
   - Lấy địa chỉ Ingress của Minikube:
     ```bash
     minikube ip
     kubectl get ingress myapp-ingress
     ```
   - Thêm vào `/etc/hosts` (hoặc `C:\Windows\System32\drivers\etc\hosts` trên Windows):
     ```
     <minikube-ip> myapp.local
     ```
     - Thay `<minikube-ip>` bằng IP từ lệnh `minikube ip`.
   - Truy cập ứng dụng: `http://myapp.local`.

10. **Triển khai bằng Helm (nếu sử dụng Helm Chart)**:
    ```bash
    helm install myapp ./myapp-chart --namespace default
    ```
    - **Giải thích**: Triển khai toàn bộ ứng dụng bằng Helm Chart thay vì các file YAML riêng lẻ.

11. **Kiểm tra triển khai**:
    - Xem Pod: `kubectl get pods`
    - Xem Service: `kubectl get svc`
    - Xem Ingress: `kubectl get ingress`
    - Xem log: `kubectl logs <pod-name>`
    - Truy cập: `http://myapp.local`
    - **Tùy chọn**: Dùng Minikube tunnel để truy cập Service/Ingress:
      ```bash
      minikube tunnel
      ```

---

### 📌 Lưu ý
- **File cấu hình**: Đảm bảo thư mục `myapp/k8s/` và các file YAML vẫn tồn tại. Nếu đã xóa, bạn cần tạo lại từ hướng dẫn trước hoặc sử dụng Helm Chart.
- **Minikube driver**: Đảm bảo driver được chọn (`docker`, `virtualbox`, v.v.) phù hợp với hệ điều hành của bạn. Kiểm tra driver hỗ trợ:
  ```bash
  minikube start --driver=help
  ```
- **Docker Hub**: Nếu dùng Docker Hub, đảm bảo `DOCKER_USERNAME` và `DOCKER_PASSWORD` đúng. Nếu dùng registry của Minikube, sử dụng `eval $(minikube docker-env)` để build image trực tiếp.
- **GitHub Actions**: Nếu bạn đã tích hợp CI/CD, cập nhật file `.github/workflows/deploy-kind.yml` để thay `kind` bằng `minikube`. Ví dụ, thay bước cài Kind bằng:
  ```yaml
  - name: Set up Minikube
    run: |
      curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
      chmod +x minikube-linux-amd64
      sudo mv minikube-linux-amd64 /usr/local/bin/minikube
      minikube start --driver=docker
  ```
- **Helm**: Nếu sử dụng Helm Chart, đảm bảo thư mục `myapp-chart/` tồn tại hoặc tạo lại theo hướng dẫn trước.

---

### 🛠 Tổng kết
**Hủy tài nguyên**:
- Xóa cụm Minikube: `minikube delete`
- Làm sạch Docker: `docker system prune -a --volumes` (tùy chọn).
- Xóa Helm release và repository: `helm uninstall`, `helm repo remove`.

**Chạy lại ứng dụng**:
- Tái tạo cụm Minikube, kích hoạt Ingress, cài Metrics Server, và triển khai lại YAML hoặc Helm Chart.
- Cấu hình `/etc/hosts` với IP của Minikube để truy cập `myapp.local`.

Nếu bạn cần thêm chi tiết, muốn điều chỉnh CI/CD cho Minikube, hoặc cần hỗ trợ một phần cụ thể (như tích hợp lại PostgreSQL hoặc Prometheus), hãy cho tôi biết!