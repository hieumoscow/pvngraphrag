# Graphrag - Công Cụ Phân Tích Văn Bản Thông Minh

## Cài Đặt và Cấu Hình

### 1. Cài Đặt
```bash
pip install graphrag
graphrag init --root ./pvn
```

### 2. Cấu Hình
1. Thêm Azure OpenAI key vào file [.env](./pvn/.env)
2. Cập nhật endpoints trong file [setting.yaml](./pvn/settings.yaml)
3. Tùy chỉnh fine tune prompts cho tiếng Việt theo PVN data:
```bash
python -m graphrag prompt-tune --root ./pvn --config ./pvn/settings.yaml --discover-entity-types --language Vietnamese
```

### 3. Tạo Index và Truy Vấn
```bash
# Tạo index cho các file markdown
python -m graphrag index --root ./pvn

# Truy vấn dữ liệu
python -m graphrag query --root ./pvn --method global --query "top 5 đề tài của dữ liệu này"
```

## Hướng Dẫn Sử Dụng Các Phương Thức Tìm Kiếm

### 1. Tìm Kiếm Tổng Quan (Global Search)
Phù hợp để:
- Tìm hiểu tổng quan về nội dung
- Xác định các chủ đề chính
- Hiểu cấu trúc tài liệu
- Tóm tắt các phần lớn của nội dung

Ví dụ:
```bash
# Tổng quan chủ đề chính
python -m graphrag query --root ./pvn --method global --query "Những chủ đề chính trong tài liệu này là gì?"

# Tóm tắt thành tựu
python -m graphrag query --root ./pvn --method global --query "Tóm tắt những thành tựu nổi bật của PVN?"

# Cấu trúc tài liệu
python -m graphrag query --root ./pvn --method global --query "Tài liệu này được cấu trúc như thế nào?"

# Sáng kiến lớn
python -m graphrag query --root ./pvn --method global --query "Những sáng kiến và dự án lớn của PVN?"

# Chiến lược tổng thể
python -m graphrag query --root ./pvn --method global --query "Chiến lược tổng thể của PVN là gì?"
```

### 2. Tìm Kiếm Chi Tiết (Local Search)
Phù hợp để:
- Tìm thông tin cụ thể về một chủ đề
- Tra cứu dữ liệu chính xác
- Tìm giải thích chi tiết
- Kiểm tra thông tin

Ví dụ:
```bash
# Chi tiết chương trình
python -m graphrag query --root ./pvn --method local --query "Chi tiết về chương trình Nhiệt Huyết Người Dầu Khí?"

# Số liệu cụ thể
python -m graphrag query --root ./pvn --method local --query "Số liệu cụ thể về kết quả kinh doanh năm 2023?"

# Chính sách chi tiết
python -m graphrag query --root ./pvn --method local --query "Chính sách phát triển nguồn nhân lực của PVN?"

# Thông tin kỹ thuật
python -m graphrag query --root ./pvn --method local --query "Các công nghệ cụ thể PVN đang sử dụng trong sản xuất?"

# Sáng kiến cụ thể
python -m graphrag query --root ./pvn --method local --query "Các biện pháp cụ thể về bảo vệ môi trường?"
```



### 3. Tìm Kiếm Liên Kết (Drift Search)
Phù hợp để:
- Tìm các khái niệm liên quan
- Khám phá mối liên hệ
- Hiểu các mối quan hệ
- Theo dõi sự phát triển của chủ đề

Ví dụ:
```bash
# Sáng kiến liên quan
python -m graphrag query --root ./pvn --method drift --query "Các hoạt động liên quan đến an sinh xã hội?"

# Dự án liên kết
python -m graphrag query --root ./pvn --method drift --query "Các dự án có liên quan đến chuyển đổi số?"

# Khám phá quan hệ
python -m graphrag query --root ./pvn --method drift --query "Mối quan hệ giữa PVN và các đối tác?"

# Kết nối chủ đề
python -m graphrag query --root ./pvn --method drift --query "Sự kết nối giữa phát triển bền vững và chiến lược kinh doanh?"

# Phát triển sáng kiến
python -m graphrag query --root ./pvn --method drift --query "Sự phát triển của văn hóa doanh nghiệp qua các giai đoạn?"
```

### Lưu Ý Khi Sử Dụng:
1. Dùng Global Search khi cần:
   - Tổng quan nội dung
   - Chủ đề chính
   - Tóm tắt chung

2. Dùng Local Search khi cần:
   - Thông tin cụ thể
   - Chi tiết chính xác
   - Trích dẫn hoặc số liệu

3. Dùng Drift Search khi muốn:
   - Khám phá mối liên hệ
   - Tìm chủ đề liên quan
   - Hiểu quan hệ giữa các chủ đề
   - Xem sự phát triển của chủ đề

## Tạo File Markdown từ Tài Liệu Gốc

Sử dụng cmd ```python ./document_analyzer.py``` để tạo các file markdown từ tài liệu trong thư mục [original_files](./docs/original_files).

## Chạy Thử

### python -m graphrag query --root ./pvn --method local --query "Các biện pháp cụ thể về bảo vệ môi trường?"

```md

SUCCESS: Local Search Response:
### Các Biện Pháp Cụ Thể Về Bảo Vệ Môi Trường

#### Chương Trình Trồng 3 Triệu Cây Xanh

Một trong những biện pháp cụ thể và nổi bật của Tập đoàn Dầu khí Việt Nam (Petrovietnam) trong việc bảo vệ môi trường là chương trình trồng 3 triệu cây xanh. Chương trình này được triển khai trong giai đoạn 2022-2025 với mục tiêu bảo vệ môi trường sinh thái, cảnh quan thiên nhiên và hạn chế ảnh hưởng tiêu cực của biến đổi khí hậu [Data: Entities (278); Relationships (305)]. Trong hai năm đầu tiên (2022-2023), Tập đoàn đã tổ chức trồng được 615.135 cây xanh trên 23 tỉnh/thành trong cả nước [Data: Sources (22)].

#### Chương Trình “Phục Hồi Rừng Trên Đất Ngập Nước”

Ngoài ra, Petrovietnam còn phát động chương trình “Phục hồi rừng trên đất ngập nước” vào ngày 24/4/2024 tại xã Trần Hợi, huyện Trần Văn Thời, tỉnh Cà Mau. Chương trình này nhằm khôi phục và bảo vệ các khu rừng ngập nước, góp phần bảo vệ đa dạng sinh học và giảm thiểu tác động của biến đổi khí hậu [Data: Entities (288); Relationships (325)]. Các đơn vị như PVGas, BSR, PVCFC, PVPower, PVTrans, VNPoly, PVD, và PQPOC đã tham gia tích cực vào chương trình này [Data: Relationships (332, 326, 327, 328, 329, 333, 330, 331)].

#### Chuyển Đổi Xanh

Petrovietnam cũng đang thực hiện sáng kiến chuyển đổi xanh, một phần trong chiến lược phát triển bền vững của mình. Sáng kiến này giúp Tập đoàn thích nghi với xu hướng chuyển đổi kép giữa chuyển đổi số và chuyển đổi xanh, nhằm giảm thiểu tác động tiêu cực đến môi trường và thúc đẩy sự phát triển bền vững [Data: Entities (88)].

#### Định Hướng Chiến Lược Sản Phẩm Mới

Định hướng chiến lược sản phẩm mới của Petrovietnam cũng được thiết kế để phù hợp với sự phát triển khoa học công nghệ, trí tuệ nhân tạo, quản trị số, và xu hướng chuyển dịch/tiết kiệm năng lượng. Điều này không chỉ giúp Tập đoàn nâng cao hiệu quả sản xuất mà còn giảm thiểu tác động tiêu cực đến môi trường [Data: Entities (89); Relationships (89)].

### Kết Luận

Những biện pháp cụ thể mà Petrovietnam đang triển khai không chỉ góp phần bảo vệ môi trường mà còn thể hiện trách nhiệm xã hội của Tập đoàn. Các chương trình trồng cây xanh, phục hồi rừng ngập nước, chuyển đổi xanh và định hướng chiến lược sản phẩm mới đều là những bước đi quan trọng trong việc bảo vệ môi trường và phát triển bền vững.

```

### python -m graphrag query --root ./pvn --method global --query "Những chủ đề chính trong tài liệu này là gì?"

```md
SUCCESS: Global Search Response:
### Chủ đề Chính trong Tài liệu về Petrovietnam

#### Trách nhiệm Xã hội của Doanh nghiệp (CSR)
Petrovietnam thể hiện cam kết mạnh mẽ đối với trách nhiệm xã hội của doanh nghiệp (CSR) thông qua các sáng kiến bảo vệ môi trường, chương trình phúc lợi xã hội, và các hoạt động văn hóa. Các hoạt động này bao gồm các chương trình hiến máu nhân đạo, hỗ trợ giáo dục, đào tạo, y tế, và phòng chống dịch bệnh [Data: Reports (32, 36, 5, 14, 23, 65, 25, 17, 44, 64, 13, 26, 30, 50)].

#### Văn hóa Tổ chức
Văn hóa tổ chức của Petrovietnam được xây dựng dựa trên các giá trị cốt lõi và tư tưởng, đạo đức, phong cách Hồ Chí Minh. Các hoạt động này được thực hiện thông qua các chỉ thị và kế hoạch của Đảng ủy Tập đoàn, bao gồm Chỉ thị 05-CT/TW và các nghị quyết liên quan [Data: Reports (32, 22, 24, 48, 45, 43, 42, 61, 62, 39, 40)].

#### Phát triển Bền vững và Đổi mới Sáng tạo
Petrovietnam tích cực tham gia vào các dự án phát triển bền vững và đổi mới sáng tạo, bao gồm các dự án lớn như nhà máy nhiệt điện Sông Hậu 1 và Thái Bình 2, và chuỗi dự án khí - điện Lô B. Các dự án này không chỉ đóng góp vào phát triển kinh tế mà còn thúc đẩy tăng trưởng bền vững [Data: Reports (32, 17)].

#### An ninh Năng lượng Quốc gia
Petrovietnam đóng vai trò quan trọng trong việc đảm bảo an ninh năng lượng quốc gia và đóng góp vào nền kinh tế, bao gồm việc duy trì việc làm và hỗ trợ phúc lợi cho nhân viên trong các thời kỳ khủng hoảng [Data: Reports (19)].

#### Giáo dục và Đào tạo
Petrovietnam và các đơn vị giáo dục và đào tạo liên quan như PVU, PVcollege, NSRP, PVE, và PVMR đóng vai trò quan trọng trong việc phát triển nguồn nhân lực và năng lực chuyên môn trong ngành dầu khí tại Việt Nam [Data: Reports (38)].

### Kết luận
Các chủ đề chính trong tài liệu này xoay quanh trách nhiệm xã hội của doanh nghiệp, văn hóa tổ chức, phát triển bền vững, an ninh năng lượng quốc gia, và giáo dục đào tạo. Những hoạt động và sáng kiến này không chỉ phản ánh cam kết của Petrovietnam đối với cộng đồng và môi trường mà còn góp phần vào sự phát triển bền vững và thịnh vượng của đất nước [Data: Reports (32, 36, 5, 14, 23, 65, 25, 17, 44, 64, 13, 26, 30, 50, 22, 24, 48, 45, 43, 42, 61, 62, 39, 40, 19, 38)].
```

### python -m graphrag query --root ./pvn --method local --query "nghi quyet 281 la gi?"

```md
SUCCESS: Local Search Response:
# Nghị quyết 281 là gì?

## Giới thiệu về Nghị quyết 281

Nghị quyết 281 là một văn bản chỉ đạo quan trọng được ban hành bởi Đảng ủy Tập đoàn Dầu khí Quốc gia Việt Nam (Petrovietnam) vào ngày 15 tháng 5 năm 2019. Nghị quyết này tập trung vào công tác truyền thông và văn hóa doanh nghiệp (TT&VHDN) trong tập đoàn, nhằm định hướng và thúc đẩy các hoạt động liên quan đến trách nhiệm xã hội của doanh nghiệp (CSR) và xây dựng văn hóa tổ chức [Data: Entities (194, 2, 24, 198)]. 

## Nội dung và mục tiêu của Nghị quyết 281

Nghị quyết 281 khẳng định tính đúng đắn của các chính sách và bổ sung thêm một số nhiệm vụ mới phù hợp với giai đoạn phát triển mới của Petrovietnam. Mục tiêu chính của nghị quyết là hướng dẫn và triển khai các hoạt động truyền thông và văn hóa doanh nghiệp, đảm bảo rằng tất cả các hoạt động của tập đoàn đều phù hợp với các mục tiêu và giá trị cốt lõi đã được xác định [Data: Entities (194, 198); Relationships (216, 223)].

## Vai trò của các cơ quan và cá nhân trong việc thực hiện Nghị quyết 281

### Tổng Giám đốc Tập đoàn

Tổng Giám đốc Tập đoàn đóng vai trò quan trọng trong việc chỉ đạo thực hiện Nghị quyết 281. Tổng Giám đốc chịu trách nhiệm tổ chức các hội nghị và ban hành các thông báo kết luận liên quan đến công tác TT&VHDN, đảm bảo rằng các chỉ đạo của nghị quyết được thực hiện một cách hiệu quả [Data: Entities (27); Relationships (27, 220, 221)].

### Ban Thường vụ Đảng ủy và Hội đồng Thành viên

Ban Thường vụ Đảng ủy và Hội đồng Thành viên cũng đóng vai trò chỉ đạo trong việc thực hiện Nghị quyết 281. Sự tham gia của các cơ quan này nhấn mạnh tầm quan trọng của sự giám sát và chỉ đạo từ cấp cao trong việc triển khai các hoạt động văn hóa và truyền thông trong tập đoàn [Data: Entities (25, 26); Relationships (25, 26)].

## Các văn bản và kết luận liên quan

### Kết luận số 234-KL/ĐU

Kết luận số 234-KL/ĐU, ban hành vào ngày 18 tháng 8 năm 2022, là một văn bản quan trọng nhằm tiếp tục đẩy mạnh thực hiện Nghị quyết 281. Kết luận này khẳng định tính đúng đắn của Nghị quyết 281 và bổ sung thêm một số nhiệm vụ mới phù hợp với giai đoạn phát triển mới của Petrovietnam [Data: Entities (195, 330); Relationships (407, 217, 219)].

### Thông báo kết luận số 5589/DKVN-TT&VHDN

Thông báo kết luận số 5589/DKVN-TT&VHDN, ban hành vào ngày 28 tháng 9 năm 2022, do Tổng Giám đốc Tập đoàn ban hành, nhằm phân công nhiệm vụ chi tiết cho các ban, đơn vị, đoàn thể trong tập đoàn để triển khai thực hiện các chỉ đạo của Nghị quyết 281 [Data: Reports (14); Relationships (220)].

## Kết luận

Nghị quyết 281 là một văn bản chỉ đạo quan trọng của Đảng ủy Tập đoàn Dầu khí Quốc gia Việt Nam, nhằm định hướng và thúc đẩy các hoạt động truyền thông và văn hóa doanh nghiệp trong tập đoàn. Sự tham gia và chỉ đạo từ các cấp lãnh đạo cao nhất của Petrovietnam đảm bảo rằng các mục tiêu và giá trị cốt lõi của tập đoàn được thực hiện một cách hiệu quả và bền vững [Data: Reports (14); Entities (194, 2, 24, 198); Relationships (216, 223, 27, 220, 221, 25, 26, 407, 217, 219)].

```