# Halüsinasyon ve RAG'in Sınırları

RAG, başlangıçta büyük ölçüde halüsinasyonu azaltmak amacıyla önerilmiş bir
yaklaşımdır: modelin cevabını, getirilen gerçek dokümanlara "topraklamak"
(grounding) fikrine dayanır. Ancak güncel araştırmalar, RAG'in halüsinasyonu
tamamen ortadan kaldırmadığını gösteriyor. Bazı hukuk alanı çalışmalarında,
RAG tabanlı araçların hâlâ önemli oranlarda hatalı/halüsine cevap
üretebildiği gözlemlenmiştir — yani RAG riski azaltır ama garanti etmez.

Halüsinasyonun RAG'de ortaya çıkabileceği birkaç tipik durum vardır: (1)
getirilen parçalar konuyla ilgili görünse de aslında soruyu cevaplamaya
yetecek kadar bilgi içermeyebilir, (2) birden fazla doküman birbiriyle
çelişen bilgiler içerebilir, (3) çok uzun bağlamlarda model, bağlamın ortasına
düşen bilgiyi gözden kaçırabilir ("lost in the middle" etkisi). Ayrıca
retrieval'ın kendisi başarısız olduğunda (yani hiç ilgili bir parça
getirilemediğinde) ya da gereksiz/yanlış bir retrieval tetiklendiğinde, bu
durum modelin halüsinasyon üretmesi için yeni bir kaynak haline gelebilir.

Bu nedenle RAG sistemleri, getirilen kaynaklarla üretilen cevap arasındaki
tutarlılığı (faithfulness/grounding) ayrıca değerlendirmeli; sadece
"retrieval doğru mu" değil, "model gerçekten getirilen bilgiye dayanarak mı
cevap verdi" sorusu da sorulmalıdır.

Kaynak: arXiv 2510.24476 ("Mitigating Hallucination in LLMs..."); arXiv
2603.07379 ("SoK: Agentic RAG..."); arXiv 2507.18910 ("A Systematic Review of
Key RAG Systems") — kavramlar bu kaynaklardan yararlanılarak yeniden
yazılmıştır.
