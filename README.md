# Görüntü Kalibrasyonu
Bu proje, OpenCV kütüphanesi kullanarak bir kameranın kalibrasyonunu yapar ve görüntülerdeki lens bozulmaları düzeltir. Kalibrasyon işlemi için satranç tahtası desenli birden fazla test görüntüsü kullanılır.

## Kamera kalibrasyonu
Kamera kalibrasyonu, bir kameranın parametrelerinin tahmin edilmesi anlamına gelir. 
kamerayla ilgili parametreler, gerçek dünyadaki bir 3B nokta ile kalibre edilmiş kamera tarafından yakalanan görüntüdeki karşılık gelen 2B izdüşümü piksel arasındaki doğru ilişkiyi belirlemek için gereklidir. 
Bu işlemde, hem içsel parametreler örneğin odak uzaklığı, optik merkez, lensin radyal bozulma katsayıları gibi, hem de dışsal parametreler kameranın gerçek dünya koordinat sistemine göre dönüşü ve ötelemesi dikkate alınmalıdır.

## 3D Nesne Projeksiyonu
Bu modelde, sahnedeki bir 3D nokta, bir perspektif dönüşüm projeksiyon ile 2D görüntü düzlemine aktarılır. Bu sayde hata tespiti gibi parametreler hesaplanabilir ve kalibrasyon etkinliği ölçülebilir.

**Temel Mantık: **

- Kamera kalibrasyonu için satranç iç köşe sayısı belirlenir.
- Köşe bulma algoritmasının durma kriterleri belirlenir.
- 3D gerçek dünya noktalarının (objpoint) ve görüntüde tespit edilen 2D noktaların (imgpoints) listelenir.
- 3D gerçek dünya noktaları ile görüntüdeki 2D noktalar eşleştirilir ve kaydedilir.
- Bu eşleşmeler kullanılarak kamera kalibrasyonu yapılır kamera matrisi ve distorsiyon katsayıları hesaplanır.
- Hesaplanan parametreler kullanılarak bozuk görüntüler düzeltilir.
- Düzeltme sonrası gereksiz kenar boşlukları kırpılır ve temiz görüntü elde edilir.
- Kalibrasyonun doğruluğunu ölçmek için 3D noktalar tekrar 2D’ye projekte edilir.
- Projeksiyon sonucu oluşan 2D noktalar ile gerçek 2D noktalar arasındaki fark hesaplanır.
- Bu farkların ortalaması ne kadar küçükse kalibrasyon o kadar başarılı olur.
- Sonuç olarak kamera lensinden kaynaklanan görüntü bozulmaları tespit edilip düzeltilir ve kaydedilir.

## Avantajları:
- Lens kaynaklı bozulmalar düzeltilir böylece daha doğru görüntüler elde edilir.
- Nesne tanıma, robotik ve artırılmış gerçeklik gibi uygulamalarda daha tutarlı sonuçlar alınır.
- kamera özellikleri hesaplanarak diğer projelerde kullanılabilir.

## Dezavantajları
- Kalibrasyon için çok sayıda farklı açıdan ve pozisyondan çekilmiş satranç tahtası gibi özel kalibrasyon görüntülerine ihtiyaç vardır.
- Köşe tespiti hatalı olursa kalibrasyon da kötü sonuç verir.
- Gerçek zamanlı uygulamalarda kalibrasyon ve düzeltilmiş görüntü oluşturma işlemci ve zaman gerektirir.

# Kamera Kalibrasyon Uygulaması

`main.py`
- Satranç tahtası görüntülerindeki köşeleri tespit edip 3D ve 2D noktalarla kameranın iç ve dış parametrelerini hesaplıyor.
- Kalibrasyon parametrelerini kullanarak verilen bir resmi (örn. '3.jpg') lens hatalarından arındırıp düzeltiyor ve kaydediyor.
- Projeksiyon hatasını hesaplayarak kalibrasyonun ne kadar başarılı olduğunu sayısal olarak veriyor.
- Hata oranı, kamera matrisi, distorsiyon katsayıları, dönüşüm ve öteleme vektörlerini ekrana basıyor.

Aşağıda Python kodu ve açıklamaları yer almaktadır.
```python
import cv2
import numpy as np
import glob

class CameraCalibrate:
    def __init__(self):
        # Satranç tahtasının iç köşe sayısı (yükseklik, genişlik)
        self.CHECKERBOARD = (6, 9)

        # Köşe bulma algoritması için durma kriteri
        self.criteria = (cv2.TERM_CRITERIA_EPS + 
                         cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # 3D (gerçek dünya) ve 2D (görüntü) noktaların listeleri
        self.objpoints = []  # Gerçek dünya noktaları
        self.imgpoints = []  # Görüntüdeki köşe noktaları

        # 3D satranç tahtası köşe koordinatları (Z = 0 düzleminde)
        self.objectp3d = np.zeros((1, self.CHECKERBOARD[0] * self.CHECKERBOARD[1], 3), np.float32)
        self.objectp3d[0, :, :2] = np.mgrid[0:self.CHECKERBOARD[0],
                                            0:self.CHECKERBOARD[1]].T.reshape(-1, 2)

        self.prev_img_shape = None
        self.mean_error = 0  # Ortalama hata (reprojection error)

    def camera_calibrate(self):
        # Bulunduğu klasördeki tüm .jpg uzantılı dosyaları al
        images = glob.glob('*.jpg')
        
        for filename in images:
            image = cv2.imread(filename)  # Görüntüyü oku
            grayColor = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Gri tona çevir
            
            # Satranç tahtasındaki köşe noktalarını bul
            ret, corners = cv2.findChessboardCorners(
                grayColor, self.CHECKERBOARD, 
                cv2.CALIB_CB_ADAPTIVE_THRESH + 
                cv2.CALIB_CB_FAST_CHECK + 
                cv2.CALIB_CB_NORMALIZE_IMAGE)
            
            if ret == True:
                # Eğer köşeler bulunduysa, 3D ve 2D noktaları listelere ekle
                self.objpoints.append(self.objectp3d)

                # Köşeleri daha hassas hale getir
                corners2 = cv2.cornerSubPix(
                    grayColor, corners, (11, 11), (-1, -1), self.criteria)

                self.imgpoints.append(corners2)

                # Köşeleri görselleştir
                image = cv2.drawChessboardCorners(image, self.CHECKERBOARD, corners2, ret)
            
            # Her resmi sırayla göster
            cv2.imshow('img', image)
            cv2.waitKey(0)

        cv2.destroyAllWindows()  # Tüm pencereleri kapat

        # Kamera kalibrasyonunu gerçekleştir
        ret, matrix, distortion, r_vecs, t_vecs = cv2.calibrateCamera(
            self.objpoints, self.imgpoints, grayColor.shape[::-1], None, None)

        return matrix, distortion, r_vecs, t_vecs

    def correction(self, img, matrix, distortion):
        # Görüntü boyutlarını al
        h, w = img.shape[:2]

        # Yeni optimize edilmiş kamera matrisi ve kırpılacak alanı (ROI) hesapla
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(matrix, distortion, (w,h), 1, (w,h))
        
        # Görüntüyü düzelt (distorsiyonu kaldır)
        dst = cv2.undistort(img, matrix, distortion, None, newcameramtx)
        
        # Kırpma işlemi (siyah kenarları kaldır)
        x, y, w, h = roi
        dst = dst[y:y+h, x:x+w]

        # Düzgün görüntüyü diske kaydet
        cv2.imwrite('output.png', dst)

    def calculate_error(self, matrix, distortion, r_vecs, t_vecs):
        # Her bir görüntü için yeniden projeksiyon hatasını hesapla
        for i in range(len(self.objpoints)):
            # 3D noktaları projekte ederek 2D görüntü noktalarına dönüştür
            imgpoints2, _ = cv2.projectPoints(self.objpoints[i], r_vecs[i], t_vecs[i], matrix, distortion)

            # Gerçek köşeler ile projekte edilen köşeler arasındaki L2 norm farkını hesapla
            error = cv2.norm(self.imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
            self.mean_error += error

            # En son hesaplanan projeksiyon sonuçlarını döndür
            return imgpoints2

    def main(self):
        # Kalibrasyon işlemi
        matrix, distortion, r_vecs, t_vecs = self.camera_calibrate()

        # Düzeltilecek örnek bir resim oku
        img = cv2.imread('3.jpg')

        # Distorsiyonu düzelt
        self.correction(img, matrix, distortion)

        # Reprojection error hesapla
        imgpoints2 = self.calculate_error(matrix, distortion, r_vecs, t_vecs)

        # Ortalama hatayı yazdır
        print("toplam hata: {}".format(self.mean_error / len(self.objpoints)))

        # Projeksiyon sonucu
        print("Projeksiyon sonucu 2D noktalar:\n", imgpoints2)

        # Kamera matrisi
        print("\n Kamera matrix:")
        print(matrix)

        # Distorsiyon katsayıları
        print("\n distortion:")
        print(distortion)

        # Rotasyon vektörleri
        print("\n rotation Vectors:")
        print(r_vecs)

        # Öteleme vektörleri
        print("\n translation Vectors:")
        print(t_vecs)

# Ana çalışma bloğu
if __name__ == '__main__':
    process = CameraCalibrate()
    process.main()

```



