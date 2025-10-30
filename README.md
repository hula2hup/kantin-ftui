# Kantin FTUI - Sistem Pemesanan Makanan Online

Website statis untuk pemesanan makanan di Kantin FTUI yang dapat dibuka langsung tanpa server.

## Cara Menggunakan Lokal

Buka file `index_static.html` di browser web Anda untuk melihat website.

## Untuk Membuat Website Dapat Diakses Publik (Oleh Siapapun)

Website ini perlu di-host secara online agar dapat diakses oleh siapapun kapan saja. Berikut langkah-langkahnya:

### Opsi 1: GitHub Pages (Gratis)

1. Buat akun GitHub jika belum punya
2. Buat repository baru dengan nama `kantin-ftui` atau nama lain
3. Upload file berikut ke repository:
   - `index_static.html`
   - Folder `static` (lengkap dengan subfolder)
4. Pergi ke **Settings** > **Pages**
5. Di bagian **Source**, pilih **Deploy from a branch**
6. Pilih branch **main** dan folder **/(root)**
7. Klik **Save**
8. Tunggu beberapa menit, lalu URL website akan muncul di bagian atas halaman Pages
9. URL akan berbentuk: `https://username.github.io/kantin-ftui/`

### Opsi 2: Netlify (Gratis)

1. Buat akun di [netlify.com](https://netlify.com)
2. Klik **Add new site** > **Deploy manually**
3. Drag and drop file `index_static.html` dan folder `static`
4. Klik **Deploy site**
5. URL akan diberikan secara otomatis

### Opsi 3: Vercel (Gratis)

1. Buat akun di [vercel.com](https://vercel.com)
2. Klik **Add New...** > **Project**
3. Import dari Git (GitHub/GitLab) atau upload manual
4. Upload file `index_static.html` dan folder `static`
5. Deploy

## Fitur Website

- ✅ Halaman utama dengan daftar toko
- ✅ Menu lengkap dari berbagai toko
- ✅ Sistem pemesanan dengan validasi jumlah (maks 20 porsi)
- ✅ Keranjang belanja menggunakan localStorage
- ✅ Desain responsif untuk mobile dan desktop
- ✅ Tidak memerlukan server backend

## Teknologi Digunakan

- HTML5
- CSS3 (dengan Google Fonts)
- JavaScript ES6

## Catatan

Website ini adalah versi statis yang tidak menyimpan data ke database. Semua pemesanan hanya disimpan di browser pengguna menggunakan localStorage.
