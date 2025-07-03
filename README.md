# Görüntü Kalibrasyonu
Bu proje, OpenCV kütüphanesi kullanarak bir kameranın kalibrasyonunu yapar ve görüntülerdeki lens bozulmaları düzeltir. Kalibrasyon işlemi için satranç tahtası desenli birden fazla test görüntüsü kullanılır.

## Kamera kalibrasyonu
Kamera kalibrasyonu, bir kameranın parametrelerinin tahmin edilmesi anlamına gelir. 
kamerayla ilgili parametreler, gerçek dünyadaki bir 3B nokta ile kalibre edilmiş kamera tarafından yakalanan görüntüdeki karşılık gelen 2B izdüşümü piksel arasındaki doğru ilişkiyi belirlemek için gereklidir. 
Bu işlemde, hem içsel parametreler örneğin odak uzaklığı, optik merkez, lensin radyal bozulma katsayıları gibi, hem de dışsal parametreler kameranın gerçek dünya koordinat sistemine göre dönüşü ve ötelemesi dikkate alınmalıdır.

## 3D Nesne Projeksiyonu
Bu modelde, sahnedeki bir 3D nokta, bir perspektif dönüşüm projeksiyon ile 2D görüntü düzlemine aktarılır. Bu sayde hata tespiti gibi parametreler hesaplanabilir ve kalibrasyon etkinliği ölçülebilir.

**Temel Mantık: **

Kamera kalibrasyonu için satranç tahtasının karelerinin köşeleri kullanılır.

Satranç tahtasının gerçek dünyadaki 3D noktaları belirlenir (Z=0 düzlemi varsayılır).

Satranç tahtasının her bir fotoğrafındaki 2D köşe noktaları tespit edilir.

3D gerçek dünya noktaları ile görüntüdeki 2D noktalar eşleştirilir ve kaydedilir.

Bu eşleşmeler kullanılarak kamera kalibrasyonu yapılır; kamera matrisi ve distorsiyon katsayıları hesaplanır.

Hesaplanan parametreler kullanılarak bozuk (distorsiyonlu) görüntüler düzeltilir.

Düzeltme sonrası gereksiz kenar boşlukları kırpılır ve temiz görüntü elde edilir.

Kalibrasyonun doğruluğunu ölçmek için 3D noktalar tekrar 2D’ye projekte edilir.

Projeksiyon sonucu oluşan 2D noktalar ile gerçek 2D noktalar arasındaki fark hesaplanır.

Bu farkların ortalaması (reprojection error) ne kadar küçükse kalibrasyon o kadar başarılıdır.

Sonuç olarak kamera lensinden kaynaklanan görüntü bozulmaları tespit edilip düzeltilir.

