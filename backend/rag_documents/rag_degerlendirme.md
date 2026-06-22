# RAG Sistemlerinin Değerlendirilmesi

Bir RAG sistemini değerlendirirken, sadece nihai cevabın doğruluğuna bakmak
yeterli değildir; çünkü RAG aslında birbirine bağlı iki ayrı sistemden
oluşur: retrieval (doğru parçaları bulma) ve generation (bu parçalara
dayanarak cevap üretme). Sadece çıktıyı değerlendirmek, hatanın hangi
aşamadan kaynaklandığını gizler. Bu yüzden değerlendirme genellikle ayrı
ayrı yapılır:

- **Retrieval kalitesi**: Getirilen parçalar, soruyu cevaplamak için gerçekten
  gerekli olan bilgiyi içeriyor mu? Doğru doküman koleksiyonda var olsa bile
  hiç getirilmemiş olabilir — bu durumda üretim aşamasının hiçbir iyileştirmesi
  sorunu çözemez.
- **Grounding/faithfulness**: Üretilen cevap, gerçekten getirilen parçalara mı
  dayanıyor, yoksa model kendi parametrik bilgisine mi kaymış?
- **Cevap doğruluğu (correctness)**: Nihai cevap, beklenen/doğru cevapla ne
  kadar örtüşüyor?

Bu üç boyutu ayrı ayrı ölçen değerlendirme setleri (benchmark'lar)
geliştirilmiştir; bazıları özellikle "gürültülü" (alakasız veya çelişkili)
bağlama karşı modelin dayanıklılığını test eder. Pratikte, bir RAG sisteminde
"çıktı yanlış" denildiğinde, asıl sorunun retrieval mi yoksa generation mı
olduğunu ayırt etmek, sistemi iyileştirmenin ilk adımıdır.

Kaynak: DEV Community, "Evaluating RAG Systems: Measuring Retrieval Quality,
Grounding, and Hallucinations"; arXiv 2506.00054 ("RAG: A Comprehensive
Survey...") — kavramlar bu kaynaklardan yararlanılarak yeniden yazılmıştır.
