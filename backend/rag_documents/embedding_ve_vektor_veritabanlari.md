# Embedding Modelleri ve Vektör Veritabanları

Embedding, bir metin parçasını sayısal bir vektöre dönüştüren işlemdir; bu
vektör, metnin anlamsal içeriğini yüksek boyutlu bir uzayda temsil eder.
Anlamca birbirine yakın iki metin (örneğin eş anlamlı ya da aynı konudan
bahseden cümleler), farklı kelimeler kullansalar bile bu vektör uzayında
birbirine yakın konumlanır. Bu özellik, RAG'in sadece anahtar kelime
eşleşmesi değil, "anlamca yakınlık" üzerinden arama yapabilmesini sağlar —
embedding'ler RAG sisteminin bir tür "hafızası" gibi çalışır.

Üretilen embedding'ler bir vektör veritabanında saklanır; bir sorgu geldiğinde
sorgu da aynı embedding modeliyle vektöre dönüştürülür ve veritabanındaki en
yakın (en benzer) vektörler bulunur — bu işleme "en yakın komşu arama"
(nearest neighbor search) denir. Embedding modelinin kalitesi, RAG sisteminin
genel başarısını doğrudan etkiler: zayıf bir embedding modeli, anlamca
alakalı parçaları bile birbirinden uzak konumlandırabilir, bu da retrieval
kalitesini düşürür.

Kaynak: Tahir Saeed, "Chunking and Embedding Strategies in RAG" (Medium);
Amir Malik, "RAG Embeddings, Chunking, and Retrieval Basics" — kavramlar bu
kaynaklardan yararlanılarak yeniden yazılmıştır.
