import asyncssh
import asyncio
import re
async def check_ssh_connection (host ,port ,username ,password ):
    try :
        async with asyncssh .connect (host =host ,port =port ,username =username ,password =password ,known_hosts =None ,connect_timeout =10 )as conn :return True ,"Успешное подключение."
    except Exception as e :return False ,f"Ошибка: {e }"
async def reboot_server (host ,port ,username ,password ):
    try :
        async with asyncssh .connect (host =host ,port =port ,username =username ,password =password ,known_hosts =None ,connect_timeout =10 )as conn :await conn .run ('sudo -S перезагрузка',input =password +'\n');return True ,"Команда на перезагрузку отправлена."
    except Exception as e :return False ,f"Ошибка: {e }"
async def shutdown_server (host ,port ,username ,password ):
    try :
        async with asyncssh .connect (host =host ,port =port ,username =username ,password =password ,known_hosts =None ,connect_timeout =10 )as conn :await conn .run ('sudo -S выключение -h сейчас',input =password +'\n');return True ,"Команда на выключение отправлена."
    except Exception as e :return False ,f"Ошибка: {e }"
async def execute_command (host ,port ,username ,password ,command ):
    try :
        async with asyncssh .connect (host =host ,port =port ,username =username ,password =password ,known_hosts =None ,connect_timeout =10 )as conn :
            result =await asyncio .wait_for (conn .run (command ,check =False ),timeout =30.0 );output =(result .stdout or "")+(result .stderr or "");return True ,output .strip ()if output else "Команда выполнена. Нет вывода."
    except asyncio .TimeoutError :return False ,"Ошибка: Таймаут выполнения (30 секунд)."
    except Exception as e :return False ,f"Ошибка выполнения: {e }"
async def list_directory (host ,port ,username ,password ,path ):
    command =f"ls -la --full-time '{path }'"
    try :
        async with asyncssh .connect (host =host ,port =port ,username =username ,password =password ,known_hosts =None ,connect_timeout =10 )as conn :
            result =await asyncio .wait_for (conn .run (command ,check =True ),timeout =15.0 );files =[]
            lines =result .stdout .strip ().split ('\n')
            for line in lines [1 :]:
                parts =re .split (r'\s+',line ,8 );
                if len (parts )<9 :continue
                perms ,_ ,owner ,group ,size ,_ ,_ ,_ ,name =parts
                if name in ('.','..','./','../'):continue
                is_dir =perms .startswith ('d')
                files .append ({"name":name .strip ('/'),"type":"dir"if is_dir else "file","size":int (size ),"permissions":perms })
            files .sort (key =lambda x :(x ['type']!='dir',x ['name']));return True ,files
    except asyncio .TimeoutError :return False ,"Тайм-аут получения списка файлов (15 секунд)."
    except Exception as e :return False ,f"Общая ошибка: {e }"
async def download_file (host ,port ,username ,password ,remote_path ):
    try :
        async with asyncssh .connect (host =host ,port =port ,username =username ,password =password ,known_hosts =None ,connect_timeout =10 )as conn :
            async with conn .start_sftp_client ()as sftp :
                stats =await sftp .stat (remote_path )
                if stats .size >50 *1024 *1024 :return False ,"Файл слишком большой (> 50 МБ)."
                async with sftp .open (remote_path ,'rb')as f :content =await f .read ();return True ,content
    except Exception as e :return False ,f"Ошибка при скачивании: {e }"
async def upload_file (host ,port ,username ,password ,file_content :bytes ,remote_path :str ):
    try :
        async with asyncssh .connect (host =host ,port =port ,username =username ,password =password ,known_hosts =None ,connect_timeout =10 )as conn :
            async with conn .start_sftp_client ()as sftp :
                async with sftp .open (remote_path ,'wb')as f :await f .write (file_content );return True ,"Файл успешно загружен."
    except Exception as e :return False ,f"Общая ошибка при загрузке: {e }"
async def get_system_info (host ,port ,username ,password ):
    info ={'hostname':'н/д','os':'н/д','kernel':'н/д','uptime':'н/д','status':'🔴 Офлайн'}
    try :
        async with asyncssh .connect (host =host ,port =port ,username =username ,password =password ,known_hosts =None ,connect_timeout =10 )as conn :
            info ['status']='🟢 Онлайн'
            cmds ={'hostname':'hostname','os':'lsb_release -ds','kernel':'uname -r','uptime':'время безотказной работы -p'}
            results =await asyncio .gather (*[conn .run (cmd ,check =True )for cmd in cmds .values ()],return_exceptions =True )
            for k ,res in zip (cmds .keys (),results ):
                if not isinstance (res ,Exception ):info [k ]=res .stdout .strip ().replace ('up ','')if res .stdout else 'н/д'
            return True ,info
    except Exception :return False ,info
async def get_system_load (host ,port ,username ,password ):
    load_info ={'cpu':'н/д','ram':'н/д','disk':'н/д'}
    try :
        async with asyncssh .connect (
        host =host ,port =port ,username =username ,password =password ,
        known_hosts =None ,connect_timeout =10
        )as conn :
            try :
                cpu_result =await conn .run ("верх -bn1 | grep 'ЦП(ы)' | awk '{print $2 + $4}'",check =True )
                load_info ['cpu']=f"{float (cpu_result .stdout .strip ()):.1f}%"
            except Exception :pass
            try :
                ram_result =await conn .run ("бесплатно -м | grep Мем | awk '{print $3\"/\"$2}'",check =True )
                load_info ['ram']=f"{ram_result .stdout .strip ()} MB"
            except Exception :pass
            try :
                disk_result =await conn .run ("дф -ч / | хвост -1 | awk '{print $3\"/\"$2\" (\"$5\")'}",check =True )
                load_info ['disk']=disk_result .stdout .strip ()
            except Exception :pass
            return True ,load_info
    except Exception as e :
        return False ,f"Ошибка подключения: {e }"