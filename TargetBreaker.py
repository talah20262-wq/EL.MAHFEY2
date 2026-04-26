import customtkinter as ctk
import time
import random
import sys
import pygame
import threading

# إعدادات الصوت (pygame)
pygame.mixer.init()
# ملاحظة: قم بتغيير هذه المسارات إلى ملفات صوتية حقيقية لديك (wav, mp3)
# alarm_sound = pygame.mixer.Sound("alarm.wav")
# success_sound = pygame.mixer.Sound("success.wav")

class AdvancedPrankTool(ctk.CTk):
    def __init__(self):
        super().__init__()

        # إعدادات النافذة (ملء الشاشة، بدون إطار)
        self.attributes('-fullscreen', True)
        self.attributes('-topmost', True) # لجعلها فوق كل النوافذ
        self.configure(fg_color="black")
        
        # كتم الصوت في البداية لتجنب التشغيل التلقائي المزعج
        self.is_sound_muted = False

        # --- المرحلة الأولى: الماتريكس وصندوق التنبيه ---
        self.matrix_canvas = ctk.CTkCanvas(self, bg="black", highlightthickness=0)
        self.matrix_canvas.pack(fill="both", expand=True)
        self.katakana = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄ"
        self.font_size = 18
        self.columns = self.winfo_screenwidth() // self.font_size
        self.rain_drops = [1] * self.columns
        self.matrix_active = True
        self.draw_matrix()

        self.alert_box = ctk.CTkFrame(self, fg_color="#001400", border_color="#0f0", border_width=2, corner_radius=10)
        self.alert_box.place(relx=0.5, rely=0.4, anchor="center")

        ctk.CTkLabel(self.alert_box, text="[ ACCESS DENIED ]", text_color="#f00", font=("Courier New", 28, "bold")).pack(pady=10)
        ctk.CTkLabel(self.alert_box, text="System Vulnerability Detected!", text_color="#0f0", font=("Courier New", 18)).pack(pady=5)
        
        self.phone_input = ctk.CTkEntry(self.alert_box, placeholder_text="أدخل رقم هاتف الهدف...", width=300, fg_color="black", text_color="#0f0", border_color="#0f0")
        self.phone_input.pack(pady=20)

        self.hack_btn = ctk.CTkButton(self.alert_box, text="إطلاق عملية الاختراق", fg_color="#0f0", text_color="black", font=("Segoe UI", 16, "bold"), hover_color="#fff", command=self.start_fake_hack)
        self.hack_btn.pack(pady=10, ipady=10)

        self.status_log = ctk.CTkTextbox(self, width=500, height=200, fg_color="black", text_color="#0f0", font=("Courier New", 14), border_width=0, corner_radius=0)
        
        # --- المرحلة الثانية: شاشة قفل الهاتف ---
        self.phone_frame = ctk.CTkFrame(self, fg_color="black", corner_radius=0)
        # ملاحظة: للحصول على "خلفية هاتف" حقيقية، ستحتاج لاستخدام `ctk.CTkImage` وتحميل صورة
        # self.phone_background = ctk.CTkImage(Image.open("phone_bg.png"), size=(400, 800))
        # self.bg_label = ctk.CTkLabel(self.phone_frame, text="", image=self.phone_background)
        # self.bg_label.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.phone_frame, text="🔒", text_color="white", font=("Segoe UI Symbol", 60)).place(relx=0.5, rely=0.2, anchor="center")
        ctk.CTkLabel(self.phone_frame, text="تم قفل الجهاز", text_color="white", font=("Segoe UI", 24)).place(relx=0.5, rely=0.3, anchor="center")
        ctk.CTkLabel(self.phone_frame, text="أدخل كلمة المرور لفك التشفير:", text_color="#bbb", font=("Segoe UI", 16)).place(relx=0.5, rely=0.4, anchor="center")

        self.passcode_entry = ctk.CTkEntry(self.phone_frame, placeholder_text="**** (4 أرقام)", font=("Courier New", 32), width=200, fg_color="#1a1a1a", text_color="white", border_color="#333", justify="center", show="*")
        self.passcode_entry.place(relx=0.5, rely=0.55, anchor="center")

        self.unlock_btn = ctk.CTkButton(self.phone_frame, text="فك القفل", fg_color="#fff", text_color="black", font=("Segoe UI", 18, "bold"), width=150, corner_radius=20, command=self.check_passcode)
        self.unlock_btn.place(relx=0.5, rely=0.7, anchor="center")

        # --- المرحلة الثالثة: شاشة هاتف المستهدف ---
        self.target_phone_frame = ctk.CTkFrame(self, fg_color="#121212", corner_radius=0)
        ctk.CTkLabel(self.target_phone_frame, text="🚀", text_color="#0f0", font=("Segoe UI Symbol", 80)).place(relx=0.5, rely=0.15, anchor="center")
        ctk.CTkLabel(self.target_phone_frame, text="[ تم تحميل هاتف المستهدف ]", text_color="#0f0", font=("Courier New", 28, "bold")).place(relx=0.5, rely=0.3, anchor="center")
        ctk.CTkLabel(self.target_phone_frame, text="النظام قيد المحاكاة... Just kidding! 😉", text_color="#0f0", font=("Segoe UI", 18)).place(relx=0.5, rely=0.5, anchor="center")
        
        exit_btn = ctk.CTkButton(self.target_phone_frame, text="خروج آمن", fg_color="#222", text_color="white", font=("Segoe UI", 14), corner_radius=20, command=self.quit)
        exit_btn.place(relx=0.5, rely=0.8, anchor="center")

    def draw_matrix(self):
        if not self.matrix_active: return
        self.matrix_canvas.delete("all")
        for i in range(len(self.rain_drops)):
            char = random.choice(self.katakana)
            x = i * self.font_size
            y = self.rain_drops[i] * self.font_size
            color = "#0F0"
            if self.rain_drops[i] < 3: color = "#AFA" # لجعل البداية أكثر سطوعاً
            
            self.matrix_canvas.create_text(x, y, text=char, fill=color, font=("Courier New", self.font_size))
            
            if self.rain_drops[i] * self.font_size > self.winfo_screenheight() and random.random() > 0.975:
                self.rain_drops[i] = 0
            self.rain_drops[i] += 1
        self.after(30, self.draw_matrix)

    def start_fake_hack(self):
        phone = self.phone_input.get()
        if not phone: return # إذا لم يتم إدخال رقم، لا تفعل شيئاً
        
        # إخفاء صندوق التنبيه
        self.alert_box.place_forget()
        self.status_log.place(relx=0.5, rely=0.5, anchor="center")
        
        # تشغيل صوت إنذار (إذا كان متوفراً)
        # if not self.is_sound_muted: alarm_sound.play()

        # تشغيل المحاكاة في خيط مستقل (Thread) لتجنب تجمد الواجهة
        threading.Thread(target=self.run_fake_simulation, args=(phone,)).start()

    def run_fake_simulation(self, phone):
        messages = [
            f"> Initializing exploit on device: {phone}...",
            "> Searching for satellites connection...",
            "> IP Address Found: 192.168.1.{random.randint(2,254)}",
            "> Bypassing 2FA Security layer...",
            "> Intercepting private keys...",
            "> Compiling device image...",
            "> [ERROR] System Traced! Switching proxies...",
            "> Attempting Final Hack...",
            "> SUCCESS: Launching remote phone viewer..."
        ]

        for i, msg in enumerate(messages):
            time.sleep(random.uniform(0.8, 2.0)) # تأخير واقعي
            # تحديث الواجهة من الخيط الرئيسي
            self.status_log.after(0, lambda m=msg: (self.status_log.insert("end", m + "\n"), self.status_log.see("end")))
            
            # تغيير لون الخلفية بشكل متقطع في النهاية لإثارة الرعب
            if i > len(messages) - 3:
                self.after(0, lambda: self.configure(fg_color="#300"))
                self.after(100, lambda: self.configure(fg_color="black"))

        # الانتقال إلى المرحلة الثانية (شاشة قفل الهاتف)
        time.sleep(2)
        self.after(0, self.show_phone_lock)

    def show_phone_lock(self):
        self.matrix_active = False # إيقاف الماتريكس لتوفير الأداء
        self.matrix_canvas.pack_forget()
        self.status_log.place_forget()
        # if not self.is_sound_muted: pygame.mixer.stop() # إيقاف صوت الإنذار

        self.phone_frame.pack(fill="both", expand=True)

    def check_passcode(self):
        code = self.passcode_entry.get()
        if code == "2009":
            # كلمة السر صحيحة -> عرض هاتف المستهدف
            # if not self.is_sound_muted: success_sound.play()
            self.phone_frame.pack_forget()
            self.target_phone_frame.pack(fill="both", expand=True)
        else:
            # كلمة السر خطأ -> وميض أحمر وتصفير الخانة
            self.passcode_entry.delete(0, 'end')
            self.passcode_entry.configure(border_color="#f00")
            self.after(100, lambda: self.passcode_entry.configure(border_color="#333"))
            self.after(200, lambda: self.passcode_entry.configure(border_color="#f00"))
            self.after(300, lambda: self.passcode_entry.configure(border_color="#333"))

    def quit(self, event=None):
        self.destroy()

if __name__ == "__main__":
    app = AdvancedPrankTool()
    # للخروج من البرنامج، يجب إما إدخال كلمة السر الصحيحة أو الضغط على ALT + F4
    app.mainloop()
