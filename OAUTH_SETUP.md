# Hướng dẫn cấu hình OAuth cho Google và Facebook

## Cấu hình Google OAuth

### Bước 1: Tạo ứng dụng trên Google Cloud Console
1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo một dự án mới hoặc chọn dự án hiện có
3. Đi tới "APIs & Services" > "Credentials"
4. Nhấp "Create Credentials" > "OAuth client ID"
5. Chọn loại ứng dụng: "Web application"
6. Thêm Authorized redirect URIs:
   - `http://localhost:5000/auth/google` (cho môi trường phát triển)
   - `https://yourdomain.com/auth/google` (cho production)

### Bước 2: Lấy Client ID và Client Secret
1. Sao chép "Client ID" và "Client Secret"
2. Tạo file `.env` trong thư mục gốc của dự án
3. Thêm các biến sau:
```
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
```

## Cấu hình Facebook OAuth

### Bước 1: Tạo ứng dụng trên Facebook Developers
1. Truy cập [Facebook Developers](https://developers.facebook.com/)
2. Nhấp "My Apps" > "Create App"
3. Chọn loại app phù hợp (Consumer)
4. Điền thông tin ứng dụng

### Bước 2: Cấu hình Facebook Login
1. Trong dashboard của app, chọn "Add Product" > "Facebook Login"
2. Chọn "Settings" trong Facebook Login
3. Thêm Valid OAuth Redirect URIs:
   - `http://localhost:5000/auth/facebook` (cho môi trường phát triển)
   - `https://yourdomain.com/auth/facebook` (cho production)

### Bước 3: Lấy App ID và App Secret
1. Đi tới "Settings" > "Basic"
2. Sao chép "App ID" và "App Secret"
3. Thêm vào file `.env`:
```
FACEBOOK_CLIENT_ID=your_facebook_app_id_here
FACEBOOK_CLIENT_SECRET=your_facebook_app_secret_here
```

## Cài đặt thư viện

Chạy lệnh sau để cài đặt các thư viện cần thiết:

```bash
pip install -r requirements.txt
```

## Chạy ứng dụng

```bash
python app.py
```

## Lưu ý quan trọng

1. **Bảo mật**: Không commit file `.env` vào Git. Thêm `.env` vào file `.gitignore`
2. **HTTPS**: Trong môi trường production, phải sử dụng HTTPS cho OAuth
3. **Redirect URI**: Đảm bảo redirect URI trong code khớp với URI đã đăng ký
4. **Môi trường phát triển**: Đối với localhost, một số provider có thể yêu cầu cấu hình đặc biệt

## Kiểm tra hoạt động

1. Khởi động server Flask
2. Mở trình duyệt và truy cập trang chủ
3. Nhấp nút "Đăng nhập" để mở modal
4. Thử đăng nhập bằng nút "Google" hoặc "Facebook"
5. Sau khi xác thực thành công, bạn sẽ được chuyển về trang chủ với trạng thái đã đăng nhập

## Xử lý lỗi thường gặp

### Lỗi "redirect_uri_mismatch"
- Kiểm tra lại redirect URI trong cấu hình OAuth provider
- Đảm bảo URL khớp chính xác (bao gồm cả http/https và port)

### Lỗi "invalid_client"
- Kiểm tra lại Client ID và Client Secret
- Đảm bảo đã load đúng biến môi trường

### Lỗi "access_denied"
- Người dùng từ chối cấp quyền
- Kiểm tra scope yêu cầu có hợp lý không
