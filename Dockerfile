# Sử dụng base image chính thức với Python 3.11
FROM python:3.11-slim-bookworm

# Thiết lập biến môi trường
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    SUPABASE_URL="" \
    SUPABASE_KEY=""
    
RUN pip install --no-cache-dir \
    beautifulsoup4==4.12.2 \
    pandas==2.0.3  # Nếu cần xử lý dữ liệu dạng bảng

RUN if [ "$ENABLE_PDF" = "true" ]; then \
    apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/* ; \
fi

# Cài đặt các phụ thuộc hệ thống (tối giản)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Thiết lập thư mục làm việc
WORKDIR /app

# Copy và cài đặt requirements trước để tận dụng layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    python -m playwright install chromium && \
    python -m playwright install-deps

# Tạo non-root user và thiết lập quyền
RUN useradd -m -u 1000 appuser && \
    mkdir -p /home/appuser/.cache/ms-playwright && \
    chown -R appuser:appuser /home/appuser

# Copy toàn bộ ứng dụng
COPY . .

# Phân quyền thư mục
RUN chown -R appuser:appuser /app

# Chuyển sang user không phải root
USER appuser

# Mở cổng Streamlit
EXPOSE 8501

# Health check cải tiến
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Lệnh khởi chạy với các tham số tối ưu
CMD ["streamlit", "run", "app.py", \
    "--server.port=8501", \
    "--server.address=0.0.0.0", \
    "--server.headless=true", \
    "--server.fileWatcherType=none", \
    "--browser.gatherUsageStats=false", \
    "--server.maxUploadSize=50"]