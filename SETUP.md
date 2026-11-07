# دليل التشغيل — الدخول بالإيميل وكلمة السر

كل الخطوات بتنعمل مرة وحدة. بعدها كل شي بيمشي لحالو.

---

## أ) Firebase (مشروع `entikbat`) — ١٠ دقايق

افتح https://console.firebase.google.com واختار المشروع **entikbat**.

1. **تفعيل الدخول بالإيميل**
   Build ← **Authentication** ← Get started ← تبويب **Sign-in method** ← **Email/Password** ← Enable ← Save.
2. **السماح لموقعك**
   Authentication ← **Settings** ← **Authorized domains** ← Add domain ← `famlove88.github.io` ← Add.
3. **حسابك أنت (الـ admin)**
   Authentication ← تبويب **Users** ← **Add user** ← إيميلك وكلمة سر قوية ← Add user.
   بعد ما ينضاف، انسخ الـ **User UID** تبعو (عمود UID بالجدول) — بتحتاجو بالخطوة ٦.
4. **إنشاء قاعدة البيانات**
   Build ← **Firestore Database** ← Create database ← اختار موقع (أي واحد، مثلاً `eur3`) ← Next ←
   **Start in production mode** ← Create.
5. **قواعد الحماية**
   Firestore ← تبويب **Rules** ← امسح كل شي ← الصق محتوى ملف `firestore.rules` كامل ← **Publish**.
6. **تسجيلك كـ admin**
   Firestore ← تبويب **Data** ← **Start collection** ← Collection ID: `admins` ← Next ←
   Document ID: **الصق الـ UID تبعك** ← Field: `name` / Type: string / Value: `المختار` ← Save.

---

## ب) GitHub (repo `Fam`) — ٥ دقايق

7. **ارفع الملفات الجديدة** فوق القديمة (Add file ← Upload files ← اسحب الملفات ← Commit):
   `index.html` ، `admin.html` ، `sw.js` ، `firestore.rules` ، `build_towns.py` ، `build_voters.py` ، `README.md` ، `SETUP.md`
   ومجلد `source/README.md` و`towns/README.md`.
   وملف الـ Action: افتح `.github/workflows/build-voters.yml` بالـ repo ← زرّ القلم (Edit) ← امسح كل شي ← الصق محتوى الملف الجديد ← Commit.
   *(الـ Action رح يشتغل فوراً ويفشل برسالة «VOTERS_KEY is missing» — طبيعي، بنكمّل الخطوات.)*
8. **ولّد مفتاح التشفير**
   افتح https://famlove88.github.io/Fam/admin.html ← فوت بإيميلك ← قسم **مفتاح تشفير البيانات** ← **توليد مفتاح جديد** ← **نسخ المفتاح**.
9. **حطّ المفتاح بـ GitHub**
   الـ repo ← **Settings** ← **Secrets and variables** ← **Actions** ← **New repository secret** ←
   Name: `VOTERS_KEY` ← Secret: الصق المفتاح ← Add secret.
10. **شغّل التحديث**
    تبويب **Actions** ← **build voters data** ← **Run workflow** ← Run workflow. انطر ٢–٤ دقايق (٣٦ قرية).
    لما يخلص بيظهر commit اسمو «update voter lists»: بينضاف `data.enc` و`towns.enc` و`towns/*.enc`، وبينحذفوا لحالهن `data.js` و`towns.js` و`towns/*.js` القدام.
11. **جرّب**: افتح https://famlove88.github.io/Fam/ ← فوت بإيميلك ← البرنامج بيفتح. إذا ظهرت رسالة، اقرأها — كل رسالة بتقول شو ناقص.

---

## ج) إضافة مستخدمين

من `admin.html` ← **إضافة مستخدم** ← الاسم + الإيميل + كلمة سر (زرّ «توليد») ← **إنشاء الحساب** ← **نسخ الرسالة** وابعتها عالواتساب.
- **أول جهاز** بيفوت منو الشخص بينربط بحسابه. جهاز تاني ما بيفتح.
- بدّل تلفونو أو مسح بيانات المتصفح؟ ← **فكّ الجهاز** من صفحة الإدارة، وبيفوت من الجهاز الجديد.
- بدك توقفو فوراً؟ ← **توقيف**: بيقفل عندو حتى لو البرنامج مفتوح قدّامو.
- نسي كلمة السر؟ ← **رابط تغيير كلمة السر** (بيوصلو إيميل من Firebase، يمكن بالـ spam) — أو هو بيكبس «نسيت كلمة السر؟» بشاشة الدخول.
- بدك تحذفو نهائياً؟ ← **حذف** من صفحة الإدارة (بيمنعو من الدخول). ولحذف الإيميل نفسو: Firebase ← Authentication ← Users ← ⋮ ← Delete account.
- لإضافة admin تاني: اعملو حساب عادي، وبعدين Firestore ← `admins` ← Add document بالـ UID تبعو (موجود تحت اسمو بصفحة الإدارة). الـ admin بيفتح من أي جهاز وما بينربط.

**ملاحظة للآيفون:** إذا الشخص فتح من Safari وبعدين عمل «Add to Home Screen» وفتح من الأيقونة، الآيفون بيعتبرها جهاز تاني (تخزين منفصل). خلّيه يختار وحدة من البداية: يا Safari يا الأيقونة. إذا انقفل، فكّ الجهاز من صفحة الإدارة.

---

## د) الخصوصية — نقطة مهمة قبل ما تعتبر الموضوع خلص

التشفير بيحمي ملفات `data.enc`. بس إذا الـ repo **Public**، بيبقى مكشوف:
- ملفات الـ **PDF** بمجلد `source/` (أي حدا بيقدر ينزّلها)،
- و**النسخ القديمة** من `data.js` و`towns/*.js` بتاريخ الـ repo (history) حتى بعد حذفها.

عندك خيارين:

**الخيار ١ — الأسهل: خلّي الـ repo خاص (Private)**
الـ repo ← Settings ← General ← آخر الصفحة **Danger Zone** ← **Change visibility** ← Private.
الموقع https://famlove88.github.io/Fam/ بيضلّ شغّال ومفتوح للعالم (مع شاشة الدخول)، بس ملفات الـ repo وتاريخو بيصيروا مخفيين.
⚠️ GitHub Pages من repo خاص بدّو اشتراك **GitHub Pro** (حوالي ٤$ بالشهر). إذا ما بدك تدفع، الخيار ٢.

**الخيار ٢ — مجاني: مستودعين**
1. اعمل repo **خاص** جديد، مثلاً `Fam-source`، وارفع فيه: مجلد `source/` (كل الـ PDF)، `build_towns.py`، `build_voters.py`، و`.github/workflows/build-voters.yml`.
2. اعمل token: صورتك (فوق يمين) ← Settings ← Developer settings ← Personal access tokens ← **Fine-grained tokens** ← Generate new token ← Repository access: Only select repositories ← `Fam` ← Permissions ← Repository permissions ← **Contents: Read and write** ← Generate ← انسخو.
3. بالـ repo الخاص `Fam-source` ← Settings ← Secrets and variables ← Actions ← أضيف ٣ secrets:
   `VOTERS_KEY` (نفس المفتاح) ، `DEPLOY_REPO` = `famlove88/Fam` ، `DEPLOY_TOKEN` = الـ token.
4. شغّل الـ Action بالـ repo الخاص (Actions ← Run workflow). هو بيبني الملفات المشفّرة وبيدفشها على `Fam` لحالو.
5. بالـ repo العام `Fam`: احذف مجلد `source/` (أو خلّي فيه بس README) وملفات `build_*.py` والـ workflow — ما عاد إلهن لزوم هونيك.
6. لتنظيف **التاريخ** من البيانات القديمة: الأسهل تحذف الـ repo العام `Fam` وتعمل واحد جديد بنفس الاسم وترفع فيه بس: `index.html`، `admin.html`، `sw.js`، `manifest.json`، الأيقونات، `README.md`، وتفعّل Pages من جديد (Settings ← Pages ← Deploy from a branch ← main / root). الرابط بيضلّ نفسو. بعدها شغّل الـ Action بالـ repo الخاص ليبعت الملفات المشفّرة.

---

## هـ) شو لازم تعرف عن الحماية (بصراحة)

- الحماية الفعلية هي **كلمة السر**. قفل الجهاز بيمنع المشاركة العادية (يبعت الإيميل وكلمة السر لرفيقو)، بس شخص تقني عندو كلمة سر صحيحة بيقدر نظرياً يوصل للبيانات من جهاز تاني. يعني: ما تعطي حساب إلا لمين بتثق فيه، وإذا شكّيت ← **توقيف** فوراً وغيّر كلمة السر.
- البيانات بتنفك بالمتصفح وبتضلّ بالذاكرة وهو مفتوح؛ ما في طريقة تمنع شخص مخوّل يصوّر الشاشة أو ينسخ.
- بعد أول دخول ناجح، البرنامج بيفتح **من دون نت** على نفس الجهاز (الملفات المشفّرة مخزّنة، والجلسة محفوظة). التوقيف أو فكّ الجهاز بيوصلو لما يرجع عالنت.
- مفاتيح Firebase الموجودة بـ `index.html` (apiKey…) مش سرّية — الحماية من الـ rules.
- الخطة المجانية (Spark) كافية جداً: البرنامج بيعمل قرائتين–تلاتة من Firestore عند كل فتح.
- إذا ولّدت مفتاح جديد من صفحة الإدارة، لازم تحدّث `VOTERS_KEY` بـ GitHub وتشغّل الـ Action؛ لحدّ ما يخلص، البرنامج بيعرض «المفتاح ما بيفتح الملفات».

## رسائل شاشة الدخول وشو معناها
| الرسالة | السبب | الحل |
|---|---|---|
| الإيميل أو كلمة السر غلط | — | تأكّد، أو «نسيت كلمة السر؟» |
| الحساب غير مفعّل بعد | الإيميل موجود بـ Authentication بس ما إلو سجل بـ `users` | الأسهل: احذفو من Authentication ← Users وأعد إنشاءو من `admin.html`. أو يدوياً: Firestore ← `users` ← Add document ← ID = الـ UID تبعو، حقول: `email` (string)، `name` (string)، `active` (boolean: true)، `deviceId` (string فاضي) |
| هالحساب موقوف | المختار وقّفو | **تفعيل** من صفحة الإدارة |
| هالحساب مربوط بجهاز آخر | بدّل جهاز/متصفح أو مسح البيانات | **فكّ الجهاز** |
| مفتاح البيانات مش موجود | ما انعمل الخطوة ٨ | ولّد المفتاح من `admin.html` |
| المفتاح ما بيفتح الملفات | المفتاح بـ Firestore غير اللي انبنيت فيه الملفات | حدّث `VOTERS_KEY` وشغّل الـ Action |
| ملفات البيانات مش موجودة على الموقع | الـ Action ما اشتغل أو فشل | Actions ← شوف الخطأ ← Run workflow |
| ما عندك صلاحية | الـ rules مش منشورة صح | أعد الخطوة ٥ |
| الدخول بالإيميل مش مفعّل | الخطوة ١ ناقصة | فعّل Email/Password |
