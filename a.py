a = """Inode Number                  Inode File Path
---------------- ------------------ ---------
        34382705 0xffff88003aa67d98 /root/anaconda-ks.cfg
"""

b = """-rw-r--r-- 1 root root 6517 May  6 02:59 vol.py"""

# print 'inode',a[109:127]
# c = b.split()
# print 'access',c[0]
# print 'size',c[4]

d = """Virtual    Physical   Name
---------- ---------- ----
0xe1b17008 0x0d6ac008 \Device\HarddiskVolume1\Documents and Settings\song\Local Settings\Application Data\Microsoft\Windows\UsrClass.dat
0xe1b0a008 0x0d6f8008 \Device\HarddiskVolume1\Documents and Settings\song\NTUSER.DAT
0xe16fd508 0x0be20508 \Device\HarddiskVolume1\Documents and Settings\LocalService\Local Settings\Application Data\Microsoft\Windows\UsrClass.dat
0xe16f8008 0x0bdb5008 \Device\HarddiskVolume1\Documents and Settings\LocalService\NTUSER.DAT
0xe16d2508 0x0b8bc508 \Device\HarddiskVolume1\Documents and Settings\NetworkService\Local Settings\Application Data\Microsoft\Windows\UsrClass.dat
0xe16cc008 0x0b918008 \Device\HarddiskVolume1\Documents and Settings\NetworkService\NTUSER.DAT
0xe151c008 0x09617008 \Device\HarddiskVolume1\WINDOWS\system32\config\software
0xe151bb60 0x0962db60 \Device\HarddiskVolume1\WINDOWS\system32\config\default
0xe151cb60 0x09617b60 \Device\HarddiskVolume1\WINDOWS\system32\config\SAM
0xe15180b0 0x095510b0 \Device\HarddiskVolume1\WINDOWS\system32\config\SECURITY
0xe124e3a8 0x059b63a8 [no name]
0xe10181f0 0x0577d1f0 \Device\HarddiskVolume1\WINDOWS\system32\config\system
0xe1007178 0x0572e178 [no name]"""

e = d.split('\n')
e = e[2:]
print e