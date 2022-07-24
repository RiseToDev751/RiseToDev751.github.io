from threading import Thread
import tkinter as tk
import tkinter.ttk as ttk
from screeninfo import get_monitors
from tkinter import messagebox
import json, sys, os, hashlib, time
from ftpretty import ftpretty
import tkinter as tk
from tkVideoPlayer import TkinterVideo
from PIL import Image

local_user = os.getlogin()



data_folder = "C:/Users/"+local_user+"/AppData/Roaming/Oynatıcı/"
content_folder = data_folder+"/contents/"
json_data_file = data_folder+"data.json"
try:
    os.mkdir(data_folder)
    os.mkdir(content_folder)
except FileExistsError:
    pass


window = tk.Tk()
window.title("Ekran Oynatıcı")
window.geometry("250x300")
window.resizable(False,False)


def set_options():


    window = tk.Tk()
    window.title("Ayarlar")
    window.geometry("250x300")
    window.resizable(False,False)



    sayac = 0
    for i in get_monitors():
        sayac+=1

    #FTP Hostname zone

    ftp_server_label = ttk.Label(window, text="Hostname:")
    ftp_server_label.pack()
    ftp_server_label.place(x=25, y=25)

    ftp_server_entry = ttk.Entry(window)
    ftp_server_entry.pack()
    ftp_server_entry.place(x=100, y=25)


    #FTP Username zone

    ftp_username_label = ttk.Label(window, text="Username:")
    ftp_username_label.pack()
    ftp_username_label.place(x=25, y=50)

    ftp_username_entry = ttk.Entry(window)
    ftp_username_entry.pack()
    ftp_username_entry.place(x=100, y=50)



    #FTP Password zone

    ftp_password_label = ttk.Label(window, text="Password:")
    ftp_password_label.pack()
    ftp_password_label.place(x=25, y=75)

    ftp_password_entry = ttk.Entry(window, show="*")
    ftp_password_entry.pack()
    ftp_password_entry.place(x=100, y=75)



    sleep_label = ttk.Label(window, text="Fotoğraf S. :")
    sleep_label.pack()
    sleep_label.place(x=25, y=120)
    spin_box = ttk.Spinbox(
        window,
        from_=0,
        to=60,
        wrap=True, width=10)

    spin_box.pack()
    spin_box.place(x=100, y=120)


    def setr_options():

        data = {
            "ftp_server":ftp_server_entry.get(),
            "ftp_username":ftp_username_entry.get(),
            "ftp_password":hashlib.sha256(ftp_password_entry.get().encode("utf-8")).hexdigest(),
            "screen_num":str(sayac),
            "sleep_num":spin_box.get()   
        }
        info = json.dumps(data)
        data_file = open(json_data_file,"w")
        data_file.write(info)
        data_file.close()
        messagebox.showinfo("Ayarlandı","Bütün ayarlarınız ayarlandı.")
        window.destroy()

    finish = ttk.Button(window,text="Ayarla",command=setr_options)
    finish.pack()
    finish.place(x=100, y=150)




    window.mainloop()



def startcmd():
    

    window = tk.Tk()
    window.resizable(False, False)
    window.title("Güvenlik Kontrolü")
    window.geometry("250x100")

    check_label = ttk.Label(window, text="Onaylamak İçin Şifreyi Girin").pack()

    
    check_entry = ttk.Entry(window, width=15)
    check_entry.pack()
    check_entry.place(x=75, y=25)


    def check_pass():
        global psw_value
        pswd = open("pswd.txt", "w")
        pswd.write(check_entry.get())
        pswd.close()
        psw_value = open("pswd.txt","r").read()
        os.remove("./pswd.txt")
        jsn_file = open(json_data_file)
        dta_file = json.load(jsn_file)
        checking_password = hashlib.sha256(psw_value.encode("utf-8")).hexdigest()
        if checking_password != dta_file["ftp_password"]:
            messagebox.showerror("Onaylanmadı","Şifre Yalnış")  
        else:
            messagebox.showinfo("Onaylandı","Bilgiler doğrulandı indirme işlemine başlanıyor. İndirme bittiğinde otomatik videolar oynayacaktır.")
            window.destroy()

    check_button = ttk.Button(window, text="Onayla", command=check_pass)
    check_button.pack()
    check_button.place(x=90, y=50)


    global screen

    window.mainloop()
    file = open(json_data_file)
    data_file = json.load(file)
    hostname = data_file["ftp_server"]
    username = data_file["ftp_username"]
    password = psw_value
    sleep_time = data_file["sleep_num"]
    screen = data_file["screen_num"]

    global files, ftp_server

    if hostname == "" or username == "" or password == "" or sleep_time == "" or screen == "":
        messagebox.showerror("Hata","Ayarlamada eksikler var. Tamamlayınız")
    ftp_server = ftpretty(hostname, username, password)

    files = []


    sayac=0
    for i in ftp_server.list("/contents/"):
        sayac+=1
        if sayac >2:
            files.append(i)


    filenm = []
    for i in files:
        filenames = i.split("/contents/")
        filenm.append(filenames)
        fl = open(content_folder+"/"+filenames[1],"w").close()
        ftp_server.get(i, content_folder+filenames[1])
    

    file_sayac = 0
    for x in os.listdir(content_folder):
        file_type = x.split(".")
        if file_type == "mp4":
            root = tk.Tk()
            def bitir(e):
                root.destroy()
            tkvideo = TkinterVideo(scaled=True, master=root)
            tkvideo.load(os.listdir(content_folder)[x])
            tkvideo.pack(expand=True, fill="both")
            tkvideo.play() # play the video
            tkvideo.bind("<<Ended>>", bitir) # when the video ends calls the loop function
            root.mainloop()

        elif file_type == "png" or file_type == "jpg" or file_type == "jpeg":
            img = Image.open(content_folder+x)
            img.show()
            time.sleep(sleep_time)

    def new_file_check():
        time.sleep(1800)
        flnames = []
        sayac = 0
        flsayac = 0
        down_sayac = 2
        for i in ftp_server.list():
            sayac+=1
            if sayac > 1:
                flnames.append(i)
        for i in files:
            flsayac+=1
        if sayac - 2 != flsayac:
            for i in flnames:
                file_name = i.split("/contents/")
                for i in files:
                    if i != file_name[1]:
                        open(content_folder+file_name[1],"w").close()
                        ftp_server.get(flnames[down_sayac])
                    down_sayac+=1


    t1=Thread(target=new_file_check)
    t1.start()


settings_btn = ttk.Button(window, text="Ayarlar", command=set_options)
settings_btn.pack()
settings_btn.place(x=90, y=50)

start_btn = ttk.Button(window, text="Başlat",command=startcmd)
start_btn.pack()
start_btn.place(x=90, y=100)

screen_label = ttk.Label(window,text=screen+" tane ekran aktif.")
screen_label.pack()
screen_label.place(x=90, y=150)




window.mainloop()