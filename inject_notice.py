#!/usr/bin/env python3
"""
ByVias P0 fix: inject affiliate disclosure notice section into 8 non-en language pages.
Additive only — no existing elements removed.
Target: /Users/seongjinpark/company/100m1s-bybias/dist/{lang}/twice-thisisfor-seoul.html
Insert point: after <p class="disc-mini" data-r46w1="1"> line
"""

import re

DIST = "/Users/seongjinpark/company/100m1s-bybias/dist"
NOLTX_URL = "https://world.nol.com/en/ticket/places/26000627/products/26007949"
KETA_URL = "https://www.k-eta.go.kr"
DATE = "2026-06-12"

# Each notice section translated per language.
# Structure mirrors ko/en exactly:
#   <section class="disc-hub" id="notice" data-r46w1="1">
#   <h2>...</h2><ul><li>...</li>×8</ul>
#   <p class="dh-site">bybias.100m1s.com</p>
#   </section>

NOTICES = {
    "ja": f"""
<section class="disc-hub" id="notice" data-r46w1="1">
<h2>ご利用案内・免責事項</h2>
<ul>
<li><b>アフィリエイトリンク</b> — 予約・商品リンクのうち <span class="aff-eg"></span> マークが付いたリンクはアフィリエイト（仲介手数料）リンクです。ご購入時にByViasが手数料を受け取る場合がありますが、ご利用者への追加費用は発生しません。アフィリエイトリンクには上記マークを表示することを原則としています。</li>
<li><b>価格変動</b> — 表示価格はおおよその相場であり、随時変動します。リアルタイムの価格・残室数は日付入力後、各予約サイトで直接ご確認ください。</li>
<li><b>予測の免責</b> — 価格・残量の予測は推定値であり、実際と異なる場合があります。予約・決済に関する最終責任はご利用者様ご本人にあります。</li>
<li><b>非公式サービス</b> — 本サイトはアーティスト・所属事務所とは無関係の非公式なスケジュール・旅行情報サービスであり、公式提携関係はありません。</li>
<li><b>入国要件（K-ETA）</b> — K-ETA・ビザ要件は国籍・政策によって頻繁に変わります。出発前に公式サイト <a href="{KETA_URL}" target="_blank" rel="noopener nofollow">k-eta.go.kr</a> でご自身の国籍の要件を直接ご確認ください。</li>
<li><b>海外カード決済</b> — 海外発行カードは国内予約サイトで3DS（追加本人認証）が失敗するケースが多いです。プリペイドカード（WOWPASSなど）の準備を推奨します。</li>
<li><b>通知機能なし</b> — 価格・売切れ通知機能はありません。残席・再販は <a href="{NOLTX_URL}" target="_blank" rel="noopener nofollow">公式予約サイト（NOL Ticket）↗</a> で直接ご確認ください。</li>
<li><b>Instagramの投稿</b> — 編集者が選んだ公開投稿であり、著作権は各投稿者に帰属します。元の投稿が削除・非公開になった場合は表示されないことがあります。</li>
<li><b>情報最終確認：<span class="dtkn">{DATE}</span></b> — 時刻・営業時間・交通情報は訪問前に公式チャンネルで再確認してください。</li>
</ul>
<p class="dh-site">bybias.100m1s.com</p>
</section>""",
    "id": f"""
<section class="disc-hub" id="notice" data-r46w1="1">
<h2>Pemberitahuan &amp; keterbukaan informasi</h2>
<ul>
<li><b>Tautan afiliasi</b> — Tautan pemesanan/produk yang ditandai <span class="aff-eg"></span> adalah tautan afiliasi (komisi). ByVias dapat menerima komisi atas pembelian yang dilakukan, tanpa biaya tambahan bagi Anda. Kami berupaya menandai setiap tautan afiliasi dengan tanda ini.</li>
<li><b>Harga berubah</b> — Harga yang ditampilkan adalah perkiraan harga pasar dan dapat berubah sewaktu-waktu. Periksa harga dan ketersediaan terkini di masing-masing penyedia setelah memasukkan tanggal.</li>
<li><b>Prakiraan</b> — Prakiraan harga dan ketersediaan adalah estimasi dan dapat berbeda dari kenyataan. Anda sepenuhnya bertanggung jawab atas pemesanan dan pembayaran.</li>
<li><b>Layanan tidak resmi</b> — ByVias adalah layanan informasi jadwal &amp; perjalanan tidak resmi, tidak terafiliasi dengan artis, agensi, atau mitra resmi.</li>
<li><b>Persyaratan masuk (K-ETA)</b> — Aturan K-ETA/visa berbeda berdasarkan kewarganegaraan dan sering berubah. Sebelum berangkat, periksa kembali aturan sesuai kewarganegaraan Anda di situs resmi <a href="{KETA_URL}" target="_blank" rel="noopener nofollow">k-eta.go.kr</a>.</li>
<li><b>Kartu luar negeri</b> — Kartu yang diterbitkan di luar negeri sering gagal 3DS (verifikasi identitas tambahan) di situs tiket Korea. Kami menyarankan untuk menyiapkan kartu prabayar (misalnya, WOWPASS).</li>
<li><b>Tidak ada notifikasi</b> — Tidak tersedia notifikasi harga atau tiket habis. Periksa tiket kembali dan penjualan ulang langsung di <a href="{NOLTX_URL}" target="_blank" rel="noopener nofollow">penjual resmi (NOL Ticket) ↗</a>.</li>
<li><b>Postingan Instagram</b> — Postingan publik yang dipilih oleh editor kami; hak cipta milik masing-masing pembuat konten, dan embed dapat menghilang jika konten asli dihapus atau diatur ke privat.</li>
<li><b>Info terakhir diverifikasi: <span class="dtkn">{DATE}</span></b> — Periksa kembali jam, jam operasional, dan transportasi di saluran resmi sebelum pergi.</li>
</ul>
<p class="dh-site">bybias.100m1s.com</p>
</section>""",
    "es": f"""
<section class="disc-hub" id="notice" data-r46w1="1">
<h2>Aviso del sitio &amp; divulgaciones</h2>
<ul>
<li><b>Enlaces de afiliados</b> — Los enlaces de reserva/producto marcados con <span class="aff-eg"></span> son enlaces de afiliado (comisión). ByVias puede ganar una comisión en las compras, sin coste adicional para usted. Intentamos marcar cada enlace de afiliado con esta insignia.</li>
<li><b>Los precios cambian</b> — Los precios mostrados son tarifas de mercado aproximadas y cambian con frecuencia. Consulte los precios y la disponibilidad en tiempo real en cada proveedor después de introducir sus fechas.</li>
<li><b>Previsiones</b> — Las previsiones de precios y disponibilidad son estimaciones y pueden diferir de la realidad. Usted es el único responsable de la reserva y el pago.</li>
<li><b>Servicio no oficial</b> — ByVias es un servicio no oficial de información de agenda y viajes, sin afiliación con artistas, agencias o socios oficiales.</li>
<li><b>Requisitos de entrada (K-ETA)</b> — Las reglas de K-ETA/visado varían según la nacionalidad y cambian con frecuencia. Antes de salir, compruebe las reglas para su nacionalidad en el sitio oficial <a href="{KETA_URL}" target="_blank" rel="noopener nofollow">k-eta.go.kr</a>.</li>
<li><b>Tarjetas del extranjero</b> — Las tarjetas emitidas fuera de Corea suelen fallar en la verificación 3DS (autenticación adicional) en sitios de venta de entradas coreanos. Recomendamos tener una tarjeta prepago (p. ej., WOWPASS) como alternativa.</li>
<li><b>Sin alertas</b> — No hay alertas de precios ni de agotamiento. Consulte directamente devoluciones y reventas en el <a href="{NOLTX_URL}" target="_blank" rel="noopener nofollow">vendedor oficial (NOL Ticket) ↗</a>.</li>
<li><b>Publicaciones de Instagram</b> — Publicaciones públicas elegidas por nuestro editor; los derechos de autor pertenecen a cada autor, y las incrustaciones pueden desaparecer si el original se elimina o se hace privado.</li>
<li><b>Información verificada por última vez: <span class="dtkn">{DATE}</span></b> — Compruebe los horarios, el horario de apertura y el transporte en los canales oficiales antes de ir.</li>
</ul>
<p class="dh-site">bybias.100m1s.com</p>
</section>""",
    "th": f"""
<section class="disc-hub" id="notice" data-r46w1="1">
<h2>ประกาศเว็บไซต์ &amp; การเปิดเผยข้อมูล</h2>
<ul>
<li><b>ลิงก์พันธมิตร</b> — ลิงก์จองหรือสินค้าที่มีเครื่องหมาย <span class="aff-eg"></span> คือลิงก์พันธมิตร (รับค่าคอมมิชชัน) ByVias อาจได้รับค่าคอมมิชชันจากการซื้อของคุณ โดยไม่มีค่าใช้จ่ายเพิ่มเติมสำหรับคุณ เราพยายามทำเครื่องหมายลิงก์พันธมิตรทุกลิงก์ด้วยป้ายนี้</li>
<li><b>ราคาเปลี่ยนแปลงได้</b> — ราคาที่แสดงเป็นอัตราตลาดโดยประมาณและเปลี่ยนแปลงได้ตลอดเวลา โปรดตรวจสอบราคาและความพร้อมจำหน่ายแบบเรียลไทม์ที่ผู้ให้บริการแต่ละรายหลังจากกรอกวันที่</li>
<li><b>การคาดการณ์</b> — การคาดการณ์ราคาและความพร้อมจำหน่ายเป็นเพียงการประมาณการและอาจแตกต่างจากความเป็นจริง คุณมีความรับผิดชอบเต็มที่ในการจองและชำระเงิน</li>
<li><b>บริการไม่เป็นทางการ</b> — ByVias เป็นบริการข้อมูลตารางงานและการเดินทางที่ไม่เป็นทางการ ไม่มีความเกี่ยวข้องกับศิลปิน บริษัทต้นสังกัด หรือพันธมิตรอย่างเป็นทางการ</li>
<li><b>ข้อกำหนดการเข้าประเทศ (K-ETA)</b> — กฎ K-ETA/วีซ่าแตกต่างกันตามสัญชาติและเปลี่ยนแปลงบ่อย ก่อนออกเดินทาง โปรดตรวจสอบกฎสำหรับสัญชาติของคุณที่เว็บไซต์อย่างเป็นทางการ <a href="{KETA_URL}" target="_blank" rel="noopener nofollow">k-eta.go.kr</a></li>
<li><b>บัตรต่างประเทศ</b> — บัตรที่ออกในต่างประเทศมักผ่านการยืนยัน 3DS ไม่ผ่านในเว็บไซต์ขายตั๋วของเกาหลี เราแนะนำให้เตรียมบัตรเติมเงิน (เช่น WOWPASS) ไว้ด้วย</li>
<li><b>ไม่มีการแจ้งเตือน</b> — ไม่มีการแจ้งเตือนราคาหรือตั๋วหมด โปรดตรวจสอบตั๋วคืนและการจำหน่ายใหม่โดยตรงที่ <a href="{NOLTX_URL}" target="_blank" rel="noopener nofollow">ผู้จำหน่ายอย่างเป็นทางการ (NOL Ticket) ↗</a></li>
<li><b>โพสต์ Instagram</b> — โพสต์สาธารณะที่บรรณาธิการของเราคัดสรรมา ลิขสิทธิ์เป็นของผู้โพสต์แต่ละคน และการฝังอาจหายไปหากต้นฉบับถูกลบหรือตั้งค่าเป็นส่วนตัว</li>
<li><b>ข้อมูลตรวจสอบล่าสุด: <span class="dtkn">{DATE}</span></b> — โปรดตรวจสอบเวลา เวลาทำการ และการเดินทางในช่องทางอย่างเป็นทางการก่อนไป</li>
</ul>
<p class="dh-site">bybias.100m1s.com</p>
</section>""",
    "pt": f"""
<section class="disc-hub" id="notice" data-r46w1="1">
<h2>Aviso do site &amp; divulgações</h2>
<ul>
<li><b>Links de afiliados</b> — Links de reserva/produto marcados com <span class="aff-eg"></span> são links de afiliado (comissão). O ByVias pode receber uma comissão nas compras, sem custo adicional para você. Procuramos marcar todos os links de afiliados com este selo.</li>
<li><b>Preços mudam</b> — Os preços exibidos são tarifas aproximadas de mercado e mudam com frequência. Verifique preços e disponibilidade em tempo real em cada fornecedor após inserir suas datas.</li>
<li><b>Previsões</b> — Previsões de preços e disponibilidade são estimativas e podem diferir da realidade. Você é o único responsável pela reserva e pagamento.</li>
<li><b>Serviço não oficial</b> — O ByVias é um serviço não oficial de informações de agenda e viagens, sem afiliação com artistas, agências ou parceiros oficiais.</li>
<li><b>Requisitos de entrada (K-ETA)</b> — As regras de K-ETA/visto variam conforme a nacionalidade e mudam com frequência. Antes de partir, verifique as regras para a sua nacionalidade no site oficial <a href="{KETA_URL}" target="_blank" rel="noopener nofollow">k-eta.go.kr</a>.</li>
<li><b>Cartões estrangeiros</b> — Cartões emitidos fora da Coreia frequentemente falham na verificação 3DS (autenticação adicional de identidade) em sites de ingressos coreanos. Recomendamos ter um cartão pré-pago (ex.: WOWPASS) disponível.</li>
<li><b>Sem alertas</b> — Não há alertas de preços ou ingressos esgotados. Verifique devoluções e revendas diretamente no <a href="{NOLTX_URL}" target="_blank" rel="noopener nofollow">vendedor oficial (NOL Ticket) ↗</a>.</li>
<li><b>Publicações do Instagram</b> — Publicações públicas selecionadas pelo nosso editor; os direitos autorais pertencem a cada criador, e os embeds podem desaparecer se o original for excluído ou definido como privado.</li>
<li><b>Informação verificada pela última vez em: <span class="dtkn">{DATE}</span></b> — Verifique horários, horário de funcionamento e transporte nos canais oficiais antes de ir.</li>
</ul>
<p class="dh-site">bybias.100m1s.com</p>
</section>""",
    "ar": f"""
<section class="disc-hub" id="notice" data-r46w1="1">
<h2>إشعار الموقع والإفصاحات</h2>
<ul>
<li><b>روابط الشراكة</b> — الروابط التي تحمل علامة <span class="aff-eg"></span> هي روابط تابعة (عمولة). قد تحصل ByVias على عمولة عند الشراء، دون أي تكلفة إضافية عليك. نسعى إلى وضع هذه العلامة على جميع روابط الشراكة.</li>
<li><b>الأسعار تتغير</b> — الأسعار المعروضة تقريبية وتتغير بشكل متكرر. تحقق من الأسعار والتوافر في الوقت الفعلي لدى كل مزود بعد إدخال تواريخك.</li>
<li><b>التوقعات</b> — توقعات الأسعار والتوافر تقديرية وقد تختلف عن الواقع. أنت المسؤول الوحيد عن الحجز والدفع.</li>
<li><b>خدمة غير رسمية</b> — ByVias هي خدمة معلومات جداول ورحلات غير رسمية، ولا علاقة لها بالفنانين أو الوكالات أو الشركاء الرسميين.</li>
<li><b>متطلبات الدخول (K-ETA)</b> — تختلف قواعد K-ETA/التأشيرة حسب الجنسية وتتغير كثيراً. قبل المغادرة، تحقق من القواعد الخاصة بجنسيتك على الموقع الرسمي <a href="{KETA_URL}" target="_blank" rel="noopener nofollow">k-eta.go.kr</a>.</li>
<li><b>البطاقات الأجنبية</b> — كثيراً ما تفشل البطاقات الصادرة خارج كوريا في التحقق 3DS (التحقق الإضافي من الهوية) على مواقع التذاكر الكورية. نوصي بتجهيز بطاقة مسبقة الدفع (مثل WOWPASS).</li>
<li><b>لا تنبيهات</b> — لا توجد تنبيهات للأسعار أو نفاد التذاكر. تحقق من إعادة بيع التذاكر مباشرة على <a href="{NOLTX_URL}" target="_blank" rel="noopener nofollow">البائع الرسمي (NOL Ticket) ↗</a>.</li>
<li><b>منشورات إنستغرام</b> — منشورات عامة اختارها محررونا؛ حقوق النشر تعود لأصحابها، وقد تختفي التضمينات إذا حُذف المنشور الأصلي أو جُعل خاصاً.</li>
<li><b>آخر تحقق من المعلومات: <span class="dtkn">{DATE}</span></b> — تحقق من المواعيد وساعات العمل والمواصلات عبر القنوات الرسمية قبل الذهاب.</li>
</ul>
<p class="dh-site">bybias.100m1s.com</p>
</section>""",
    "vi": f"""
<section class="disc-hub" id="notice" data-r46w1="1">
<h2>Thông báo trang web &amp; công bố thông tin</h2>
<ul>
<li><b>Liên kết liên kết (affiliate)</b> — Các liên kết đặt phòng/sản phẩm có nhãn <span class="aff-eg"></span> là liên kết affiliate (hoa hồng). ByVias có thể nhận hoa hồng từ các giao dịch mua, mà không phát sinh thêm chi phí cho bạn. Chúng tôi cố gắng gắn nhãn này cho tất cả các liên kết affiliate.</li>
<li><b>Giá thay đổi</b> — Giá hiển thị là mức giá thị trường ước chừng và thay đổi thường xuyên. Kiểm tra giá và tình trạng phòng trống theo thời gian thực tại từng nhà cung cấp sau khi nhập ngày của bạn.</li>
<li><b>Dự báo</b> — Dự báo về giá và tình trạng sẵn có chỉ là ước tính và có thể khác thực tế. Bạn hoàn toàn chịu trách nhiệm về việc đặt phòng và thanh toán.</li>
<li><b>Dịch vụ không chính thức</b> — ByVias là dịch vụ thông tin lịch trình &amp; du lịch không chính thức, không liên kết với nghệ sĩ, công ty quản lý hay đối tác chính thức nào.</li>
<li><b>Yêu cầu nhập cảnh (K-ETA)</b> — Quy định K-ETA/thị thực khác nhau theo quốc tịch và thay đổi thường xuyên. Trước khi khởi hành, hãy kiểm tra lại quy định dành cho quốc tịch của bạn tại trang web chính thức <a href="{KETA_URL}" target="_blank" rel="noopener nofollow">k-eta.go.kr</a>.</li>
<li><b>Thẻ nước ngoài</b> — Thẻ phát hành ngoài Hàn Quốc thường thất bại xác minh 3DS (xác thực danh tính bổ sung) trên các trang bán vé Hàn Quốc. Chúng tôi khuyến nghị chuẩn bị thẻ trả trước (ví dụ: WOWPASS).</li>
<li><b>Không có thông báo</b> — Không có thông báo về giá hay vé hết. Kiểm tra vé trả lại và mở bán lại trực tiếp tại <a href="{NOLTX_URL}" target="_blank" rel="noopener nofollow">người bán chính thức (NOL Ticket) ↗</a>.</li>
<li><b>Bài đăng Instagram</b> — Các bài đăng công khai do biên tập viên của chúng tôi lựa chọn; bản quyền thuộc về từng tác giả, và phần nhúng có thể biến mất nếu bài gốc bị xóa hoặc đặt ở chế độ riêng tư.</li>
<li><b>Thông tin xác minh lần cuối: <span class="dtkn">{DATE}</span></b> — Kiểm tra lại giờ, giờ mở cửa và phương tiện di chuyển trên các kênh chính thức trước khi đến.</li>
</ul>
<p class="dh-site">bybias.100m1s.com</p>
</section>""",
    "zh-tw": f"""
<section class="disc-hub" id="notice" data-r46w1="1">
<h2>網站聲明與揭露</h2>
<ul>
<li><b>聯盟連結</b> — 預訂/商品連結中標有 <span class="aff-eg"></span> 標誌的連結為聯盟（佣金）連結。ByVias 可能在您購買時賺取佣金，您無需支付額外費用。我們致力於在每個聯盟連結上標示此標誌。</li>
<li><b>價格變動</b> — 顯示的價格為大致市場行情，隨時可能變動。請在輸入日期後，直接向各預訂平台查詢即時價格和可用性。</li>
<li><b>預測免責</b> — 價格和可用性預測僅為估算，可能與實際情況不同。預訂及付款的最終責任由使用者本人承擔。</li>
<li><b>非官方服務</b> — ByVias 是與藝人、經紀公司或官方合作夥伴無關的非官方行程及旅遊資訊服務。</li>
<li><b>入境要求（K-ETA）</b> — K-ETA/簽證規定因國籍和政策而異，且經常變動。出發前，請於官方網站 <a href="{KETA_URL}" target="_blank" rel="noopener nofollow">k-eta.go.kr</a> 確認您的國籍所適用的規定。</li>
<li><b>海外信用卡</b> — 在韓國售票網站上，海外發行的信用卡常因 3DS（額外身份驗證）而失敗。建議備妥預付卡（如 WOWPASS）。</li>
<li><b>無通知功能</b> — 本站不提供價格或售罄通知功能。請直接至 <a href="{NOLTX_URL}" target="_blank" rel="noopener nofollow">官方售票商（NOL Ticket）↗</a> 確認退票及補售資訊。</li>
<li><b>Instagram 貼文</b> — 由編輯精選的公開貼文，著作權歸各貼文者所有，若原始貼文遭刪除或設為私人，嵌入內容可能無法顯示。</li>
<li><b>資訊最終確認日期：<span class="dtkn">{DATE}</span></b> — 前往前請於官方頻道再次確認時間、營業時間及交通資訊。</li>
</ul>
<p class="dh-site">bybias.100m1s.com</p>
</section>""",
    "zh-cn": f"""
<section class="disc-hub" id="notice" data-r46w1="1">
<h2>网站声明与披露</h2>
<ul>
<li><b>联盟链接</b> — 预订/商品链接中标有 <span class="aff-eg"></span> 标志的链接为联盟（佣金）链接。ByVias 可能在您购买时获得佣金，您无需承担额外费用。我们致力于在每个联盟链接上标注此标志。</li>
<li><b>价格变动</b> — 显示的价格为大致市场行情，随时可能变动。请在输入日期后，直接向各预订平台查询实时价格和可用性。</li>
<li><b>预测免责</b> — 价格和可用性预测仅为估算，可能与实际情况不同。预订及付款的最终责任由用户本人承担。</li>
<li><b>非官方服务</b> — ByVias 是与艺人、经纪公司或官方合作伙伴无关的非官方行程及旅游信息服务。</li>
<li><b>入境要求（K-ETA）</b> — K-ETA/签证规定因国籍和政策而异，且经常变动。出发前，请在官方网站 <a href="{KETA_URL}" target="_blank" rel="noopener nofollow">k-eta.go.kr</a> 核实您的国籍所适用的规定。</li>
<li><b>境外信用卡</b> — 在韩国售票网站上，境外发行的信用卡常因 3DS（额外身份验证）而失败。建议备好预付卡（如 WOWPASS）。</li>
<li><b>无通知功能</b> — 本站不提供价格或售罄通知功能。请直接前往 <a href="{NOLTX_URL}" target="_blank" rel="noopener nofollow">官方售票商（NOL Ticket）↗</a> 查询退票及补售信息。</li>
<li><b>Instagram 帖子</b> — 由编辑精选的公开帖子，版权归各发帖者所有，若原帖被删除或设为私密，嵌入内容可能无法显示。</li>
<li><b>信息最终确认日期：<span class="dtkn">{DATE}</span></b> — 前往前请在官方渠道再次确认时间、营业时间及交通信息。</li>
</ul>
<p class="dh-site">bybias.100m1s.com</p>
</section>""",
}

DISC_MINI_PATTERN = re.compile(
    r'(<p class="disc-mini" data-r46w1="1">.*?</p>)', re.DOTALL
)

results = []
for lang, notice_html in NOTICES.items():
    fpath = f"{DIST}/{lang}/twice-thisisfor-seoul.html"
    with open(fpath, encoding="utf-8") as f:
        content = f.read()

    # Safety: already injected?
    if 'id="notice"' in content:
        results.append((lang, "SKIP - already has notice"))
        continue

    # Find disc-mini and insert notice after it
    match = DISC_MINI_PATTERN.search(content)
    if not match:
        results.append((lang, "ERROR - disc-mini not found"))
        continue

    insert_pos = match.end()
    new_content = content[:insert_pos] + "\n" + notice_html + content[insert_pos:]

    with open(fpath, "w", encoding="utf-8") as f:
        f.write(new_content)

    results.append((lang, "OK"))

for lang, status in results:
    print(f"  {lang}: {status}")
