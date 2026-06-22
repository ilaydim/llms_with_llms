# Chunking Stratejileri

RAG sistemlerinde dokümanlar, retrieval öncesinde "chunk" adı verilen küçük
parçalara bölünür; çünkü embedding modelleri genelde uzun paragraflardan çok
kısa metin birimlerinde (cümle veya birkaç cümlelik bloklar) daha iyi anlam
temsili üretir. Chunk boyutu, sistemin hem bağlamı koruma hem de arama
hassasiyeti arasındaki dengeyi belirler: chunk çok küçük olursa cümleler
bağlamından kopar ve embedding anlamı tam yakalayamaz; chunk çok büyük olursa
parça içine alakasız bilgi karışır, bu da arama sırasında yanlış parçaların
"en yakın" çıkmasına yol açabilir.

Basit yaklaşım sabit boyutlu (fixed-size) chunking'dir — metni belirli bir
token/karakter sayısında böler. Daha gelişmiş yaklaşımlar ise semantik
chunking (anlam sınırlarına göre bölme) veya doküman hiyerarşisine göre bölme
(başlık/alt başlık yapısını koruyarak) gibi yöntemlerdir. Hangi stratejinin
en iyi performansı verdiği; doküman türüne, sorgu tipine ve kullanılan
embedding modeline göre değişir — yani "tek doğru chunk boyutu" yoktur,
deneysel olarak ayarlanması gerekir.

Kaynak: Tahir Saeed, "Chunking and Embedding Strategies in RAG" (Medium);
Wikipedia, "Retrieval-augmented generation" maddesi — kavramlar bu
kaynaklardan yararlanılarak yeniden yazılmıştır.
