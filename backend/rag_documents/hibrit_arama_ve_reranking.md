# Hibrit Arama ve Re-ranking

Sadece embedding tabanlı (dense) arama bazı durumlarda yetersiz kalabilir:
sorgudaki spesifik bir terim (örneğin bir ürün kodu, bir yıl ya da özel bir
isim) embedding uzayında "anlamca" öne çıkmayabilir, çünkü dense arama
genelleyici/anlamsal benzerliğe odaklanır. Bu nedenle pratikte, dense
(embedding tabanlı) arama ile sparse (anahtar kelime tabanlı, örn. BM25
algoritması) arama birlikte kullanılır — buna hibrit arama denir. BM25, bir
terimin dokümanda ne sıklıkla geçtiğine ve koleksiyon genelinde ne kadar nadir
olduğuna bakarak klasik bir alaka skoru hesaplar.

İki farklı arama yönteminden gelen sonuçlar genellikle "Reciprocal Rank
Fusion" (RRF) gibi bir yöntemle birleştirilir. Bulunan adaylar genellikle
sayıca fazladır ve hepsi eşit kalitede değildir; bu yüzden üçüncü bir adım
olarak bir "re-ranker" (genellikle bir cross-encoder modeli), sorgu-doküman
çiftini daha pahalı ama daha hassas bir şekilde yeniden puanlayarak en
alakalı parçaları öne çıkarır. Özetle: hibrit arama "doğru adayları
yakalama" (recall), re-ranking ise "en iyilerini öne çıkarma" (precision)
görevini üstlenir.

Kaynak: Atlan, "Hybrid RAG: Dense and Sparse Retrieval for Better AI
Answers"; Superlinked VectorHub, "Optimizing RAG with Hybrid Search &
Reranking" — kavramlar bu kaynaklardan yararlanılarak yeniden yazılmıştır.
