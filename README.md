# Teknologi Komputasi Awan

## Anggota Kelompok

| NRP | Nama |
|-----|------|
| 5027241045 | Ivan Syarifuddin |
| 5027241053 | Oscaryavat Viryavan |
| 5027241056 | Theodorus Aaron Ugraha |
| 5027241057 | Ananda Fitri Wibowo |
| 5027241075 | Muhammad Farrel Rafli Al Fasya |
| 5027241091 | Muhammad Ardiansyah Tri Wibowo |
| 5027241106 | Mohammad Abyan Ranuaji |
| 5027241109 | Raynard Carlent |

---

## Daftar Isi

1. [Introduction](#1-introduction)
2. [Arsitektur Cloud](#2-arsitektur-cloud)
   * [Diagram Topologi](#diagram-topologi)
   * [Spesifikasi dan Estimasi Harga VM](#spesifikasi-dan-estimasi-harga-vm)
3. [Implementasi](#3-implementasi)
   * [Konfigurasi Database Server (VM 4)](#konfigurasi-database-server-vm-4)
   * [Konfigurasi Application Server (VM 2 dan VM 3)](#konfigurasi-application-server-vm-2-dan-vm-3)
   * [Konfigurasi Web Server dan Load Balancer (VM 1)](#konfigurasi-web-server-dan-load-balancer-vm-1)
4. [Hasil Pengujian Endpoint](#4-hasil-pengujian-endpoint)
   * [Pengujian API via Postman](#pengujian-api-via-postman)
   * [Tampilan Antarmuka Frontend](#tampilan-antarmuka-frontend)
5. [Hasil Load Testing](#5-hasil-load-testing)
   * [Analisis Strategi Load Balancing](#analisis-strategi-load-balancing)
   * [Pencarian Peak Concurrency (Skenario 2 hingga 5)](#pencarian-peak-concurrency-skenario-2-hingga-5)
6. [Kesimpulan dan Saran](#6-kesimpulan-dan-saran)

---

## 1. Introduction

Laporan ini disusun untuk memenuhi tugas Final Project mata kuliah Teknologi Komputasi Awan. Permasalahan utama yang diangkat adalah kebutuhan untuk mendeploy aplikasi Order Processing Service yang bersifat *write-heavy* ke lingkungan *production* di *cloud*. Aplikasi ini harus mampu menangani lonjakan beban *request* yang tinggi dari pengguna secara bersamaan tanpa mengalami kegagalan sistem.

Tujuan dari proyek ini adalah merancang dan mengimplementasikan arsitektur *cloud* terdistribusi (High Availability) yang mencakup lapisan Web Server, Load Balancer, Application Server, dan Database Server. Evaluasi dilakukan melalui serangkaian *load testing* eksternal untuk menentukan konfigurasi terbaik dan mengetahui batas maksimal kemampuan sistem dalam menangani lalu lintas pengguna yang simultan.

---

## 2. Arsitektur Cloud

### Diagram Topologi

Kelompok kami mengimplementasikan arsitektur *3-tier* terdistribusi di lingkungan *cloud*. Nginx digunakan sebagai *web server* sekaligus *load balancer* (gerbang utama) yang membagi beban lalu lintas ke dua *application server* Flask. Kedua *application server* tersebut kemudian berkomunikasi dengan satu database server MongoDB terpusat.

Berikut adalah diagram diagram topologi rancangan kami:

<img width="970" height="544" alt="image" src="https://github.com/user-attachments/assets/cb32dfcc-2e37-4875-ad8a-eacda78fc6d0" />

Diagram di atas menunjukkan aliran data dari Internet (melalui port 80 ke Nginx), diteruskan ke Application Tier (melalui port 5000), dan akhirnya berinteraksi dengan Database Tier (melalui port 27017).

### Spesifikasi dan Estimasi Harga VM

Untuk implementasi ini, kami menggunakan empat Virtual Machine (VM) di penyedia layanan *cloud* Azure, dengan rincian spesifikasi dan estimasi harga sebagai berikut:

| Peran VM | Nama VM | Spesifikasi (vCPU/RAM) | Estimasi Harga/Bulan (Per VM) | Total Harga (Lapis) |
| :--- | :--- | :--- | :--- | :--- |
| Web & Load Balancer | VM 1 | Standard B1ls (1 vCPU, 0.5 GB RAM) | $3.80 | $3.80 |
| Application Server | VM 2, VM 3 | Standard B2s (2 vCPU, 4 GB RAM) | $30.66 | $61.32 |
| Database Server | VM 4 | Standard B1s (1 vCPU, 1 GB RAM) | $7.59 | $7.59 |
| **Total** | | | | **$72.71** |

---

## 3. Implementasi

Seluruh kode sumber dan *script* otomasi *deployment* dapat ditemukan pada *repository* ini. Folder `resources` berisi file aplikasi Flask (BE), file *static* frontend (FE), serta *script* database (DB) dan pengujian (Test). Perintah `deploy_all.sh` digunakan untuk mengotomatisasi proses instalasi di seluruh VM.

### Konfigurasi Database Server (VM 4)

1.  VM 4 dikonfigurasi untuk menjalankan MongoDB Server. Port 27017 dibuka pada *network security group* agar dapat diakses oleh VM Application Server.
2.  Data awal di-*restore* menggunakan *script* `generate_dump.py` atau `mongorestore` dari folder `resources/DB/dump`.
3.  Tangkapan layar di bawah menunjukkan proses pembersihan database menggunakan *script* `cleanup.sh` yang dijalankan dari jarak jauh untuk memastikan validitas pengujian beban.

<placeholder>

### Konfigurasi Application Server (VM 2 dan VM 3)

1.  VM 2 dan VM 3 menjalankan aplikasi Flask. Dependensi diinstal menggunakan `pip install -r resources/BE/requirements.txt`.
2.  Aplikasi dijalankan menggunakan Gunicorn sebagai WSGI *server* dengan konfigurasi 9 *workers* (`-w 9 -b 0.0.0.0:5000`) untuk memaksimalkan penggunaan vCPU yang tersedia.
3.  Variabel lingkungan dikonfigurasi agar aplikasi terhubung ke IP VM 4 (Database).
4.  Berikut adalah tampilan `htop` pada VM Backend 1 (VM 2) yang menunjukkan beban kerja proses Python/Gunicorn saat menahan beban tinggi.

<img width="861" height="435" alt="skenario3 (5)" src="https://github.com/user-attachments/assets/c19dcfff-2202-4030-9002-1435cd65575e" />

<img width="859" height="428" alt="skenario5 (5)" src="https://github.com/user-attachments/assets/ba7402f0-d1d6-4335-a18e-508298af135e" />

### Konfigurasi Web Server dan Load Balancer (VM 1)

1.  VM 1 menjalankan Nginx di dalam *container* Docker (`nginx-lb`). Port 80 dibuka untuk publik.
2.  File `nginx.conf` dikonfigurasi untuk mendeploy file *static* frontend (`index.html`, `styles.css`) di lokasi `/usr/share/nginx/html`.
3.  Nginx juga dikonfigurasi sebagai Reverse Proxy dan Load Balancer. Bagian `upstream` diarahkan ke IP VM 2 dan VM 3 pada port 5000.
4.  Berikut adalah tangkapan layar `htop` pada VM 1 yang menunjukkan utilisasi Nginx yang sangat rendah meskipun menangani ribuan *request*, membuktikan efisiensi Nginx sebagai *load balancer*.

<img width="861" height="435" alt="skenario3 (5)" src="https://github.com/user-attachments/assets/c19dcfff-2202-4030-9002-1435cd65575e" />

---

## 4. Hasil Pengujian Endpoint

### Pengujian API via Postman

Kami menguji keempat *endpoint* API utama menggunakan Postman untuk memastikan fungsionalitas aplikasi berjalan lancar sebelum dilakukan pengujian beban.

* **POST /order:** Berhasil membuat pesanan baru (Status 201 Created).

![Placeholder untuk Screenshot Postman POST order](path/to/image_postman_post.png)

* **GET /order/<id>:** Berhasil mengambil detail pesanan spesifik (Status 200 OK).

![Placeholder untuk Screenshot Postman GET order id](path/to/image_postman_get_id.png)

* **GET /orders:** Berhasil mengambil riwayat seluruh pesanan (Status 200 OK).

![Placeholder untuk Screenshot Postman GET orders](path/to/image_postman_get_all.png)

* **PUT /order/<id>:** Berhasil memperbarui status pesanan (Status 200 OK).

![Placeholder untuk Screenshot Postman PUT order id](path/to/image_postman_put.png)

### Tampilan Antarmuka Frontend

Aplikasi frontend sederhana dikembangkan untuk merepresentasikan interaksi pengguna dengan keempat *endpoint* API tersebut. Tampilan visual antarmuka ini telah sesuai dengan file `index.html` dan `styles.css` yang dideploy di VM 1.

![Placeholder untuk Screenshot Tampilan Web Frontend](path/to/image_web_frontend.png)

---

## 5. Hasil Load Testing

Pengujian beban dilakukan menggunakan alat Locust yang dijalankan dari mesin eksternal. *File script* yang digunakan adalah `resources/Test/locustfile.py`, yang difokuskan pada simulasi transaksi *order* sesuai target *endpoint*.

### Analisis Strategi Load Balancing

Skenario 1 digunakan untuk menguji algoritma terbaik. Kami membandingkan tiga strategi *load balancing* Nginx dengan jumlah *user* bertahap. Hasil RPS (*Requests Per Second*) agregat menunjukkan bahwa algoritma **Round Robin** memberikan hasil tertinggi dan paling stabil.

* **Round Robin (Pemenang):** RPS agregat mencapai **116.92** dengan *Response Time* Meditasi 850ms.
* Least Connection: RPS agregat **107.03**.
* IP Hash: RPS agregat **111.45**.

Oleh karena itu, seluruh pengujian selanjutnya dikunci menggunakan algoritma Round Robin.

### Pencarian Peak Concurrency (Skenario 2 hingga 5)

Kami melakukan serangkaian uji coba untuk menemukan batas maksimal pengguna simultan (*Peak Concurrency*) yang bisa ditangani oleh sistem dengan kriteria **0% Failure Rate** (0 kegagalan). Skenario 2 hingga 5 memiliki *Spawn Rate* (kecepatan masuknya user baru) yang semakin brutal.

Berikut adalah rekapitulasi hasil pencarian *Peak Concurrency* kelompok kami:

* **Skenario 2 (Spawn Rate 50):** Berhasil menahan beban **1000 User** tanpa kegagalan (0 Fails).

<img width="849" height="385" alt="skenario2 (7)" src="https://github.com/user-attachments/assets/3ee843c5-e405-4bbd-9ec2-4b2bb8e06afa" />

<img width="916" height="291" alt="skenario2 (9)" src="https://github.com/user-attachments/assets/ee7e0bf2-c3be-4bbd-823d-8fd6b2c65143" />

* **Skenario 3 (Spawn Rate 100):** Berhasil menahan beban **2500 User** tanpa kegagalan (0 Fails).

<img width="918" height="283" alt="skenario3 (12)" src="https://github.com/user-attachments/assets/8d81cb50-c905-40d9-b7b4-4dd21f70e2cb" />

<img width="847" height="323" alt="skenario3 (10)" src="https://github.com/user-attachments/assets/b6271ffc-07b4-42fb-8486-c439901aec83" />

* **Skenario 4 (Spawn Rate 200):** Berhasil menahan beban **4000 User** tanpa kegagalan (0 Fails).

<img width="911" height="289" alt="skenario4 (6)" src="https://github.com/user-attachments/assets/d389e4e3-ae22-4765-bbcc-6c31d062331d" />

<img width="848" height="333" alt="skenario4 (4)" src="https://github.com/user-attachments/assets/c2fe5455-6774-496c-aba6-ea430c634b65" />

* **Skenario 5 (Spawn Rate 500 - Ekstrem):** Berhasil menahan beban **1500 User** tanpa kegagalan (0 Fails). Meskipun dicoba di angka 2000, 2500, dan 5000 User menghasilkan *error* jaringan (Error 0), server berhasil *recover* dan mencetak angka Meditasi RPS **145.82** di titik 1500 User.

<img width="917" height="295" alt="skenario5 (6)" src="https://github.com/user-attachments/assets/5aa9c63f-6b82-44a4-bf76-7ece68f0bfd2" />

<img width="854" height="337" alt="skenario5 (4)" src="https://github.com/user-attachments/assets/34901e1e-4fc9-4963-8be4-829f3375628e" />

---

## 6. Kesimpulan dan Saran
