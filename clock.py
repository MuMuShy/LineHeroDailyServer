from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='mon-sun',hour='0')
def scheduled_job():
    from DataBase import DataBase
    dataBase = DataBase()
    print("12.00過後每日任務重置")
    dataBase.clearDailyRequest()

#檢查拍賣場是否有過期拍賣
@sched.scheduled_job('cron',minute='*')
def scheduled_job_auctioncheck():
    from DataBase import DataBase
    from datetime import datetime, timedelta
    import math
    dataBase = DataBase()
    print(":SERVER:-- 拍賣系統檢查 --")
    _auctionlist = dataBase.getAuctionList("weapon")
    if _auctionlist is None or len(_auctionlist) == 0:
        print(":SERVER:-- 拍賣系統檢查 -- 無架上物品")
    else:
        for auction in _auctionlist:
            auction_info = auction["auction_info"]
            _starttime = auction_info["auction_start_time"]
            #時間處裡
            current =  datetime.now()
            _begintime = datetime.strptime(_starttime,"%m/%d/%Y %H:%M:%S")
            time_elapsed = (current-_begintime) #經過的掛機時間
            time_elapsed = math.floor(time_elapsed.total_seconds())
            if time_elapsed > 86400 : #如果超過24小時 要下架
                print(":SERVER: --拍賣系統-- 過期商品: ID:"+str(auction_info["auction_id"]))
                #加回使用者
                line_id = auction_info["auction_line_id"]
                _weapon_info = auction["weapon_json"]
                hassame,loc = dataBase.checkUserPackMaxLoc(line_id,"weapon",_weapon_info["weapon_id"])
                dataBase.addToUserBackPack(line_id,"weapon",_weapon_info["weapon_id"],1,hassame,loc)
                dataBase.addToUserWeaponWithEnhanced(line_id,_weapon_info["weapon_id"],loc,auction_info["str_add"],auction_info["int_add"],
                auction_info["dex_add"],auction_info["atk_add"],auction_info["uses_reel"],auction_info["available_reeltime"],auction_info["description"],auction_info["success_time"])
                #移除拍賣場訂單
                dataBase.removeAuction(auction_info["auction_id"],auction_info["auction_line_id"])
                print(":SERVER: --拍賣系統-- 過期商品: ID:"+str(auction_info["auction_id"])+" 歸還成功")
    print(":SERVER:-- 拍賣系統檢查 -- 完成")

#檢查世界王遠征軍
@sched.scheduled_job('cron',minute='10')
def scheduled_job_WordArmycheck():
    print(":SERVER:-- 世界王系統檢查 遠征軍 -- ")
    from DataBase import DataBase
    from datetime import datetime, timedelta
    import math
    dataBase = DataBase()
    _bossstatus = dataBase.getWordBossStatus()
    if _bossstatus is None:
        print(":SERVER:-- 世界王已消滅 重置")
        dataBase.startWordBoss(0)
    else:
        print(":SERVER:-- 世界王進行遠征軍傷害檢查 -- ")
        if _bossstatus["last_word_army"] is None:
            print("尚未出發過遠征軍 立即出發")
            dataBase.ArmyDamageWordBoss()
        else:
            current =  datetime.now()
            _lastarmytime = _bossstatus["last_word_army"]
            _lasttime = datetime.strptime(_lastarmytime,"%m/%d/%Y %H:%M:%S")
            time_elapsed = (current-_lasttime) #經過的掛機時間
            time_elapsed = math.floor(time_elapsed.total_seconds())
            print("經過秒數:"+str(time_elapsed))
            if time_elapsed >= 3590: #每小時攻擊一次
                print("遠征軍冷卻時間到 遠征軍出發")
                dataBase.ArmyDamageWordBoss()
            else:
                print("遠征軍還在準備中")
            print("遠征軍檢查-- 完成")

@sched.scheduled_job('cron',minute='*')
def scheduled_job_Bosscheck():
    print(":SERVER:-- 世界王系統檢查 -- ")
    from DataBase import DataBase
    from datetime import datetime, timedelta
    import math
    dataBase = DataBase()
    _bossstatus = dataBase.getWordBossStatus()
    if _bossstatus is None:
        print(":SERVER:-- 世界王已消滅")
        #dataBase.startWordBoss(0)
    else:
        print(":SERVER:-- 世界王進行傷害check -- ")
        totaldamage =dataBase.getWordBossNowTotalDamage()
        print(":SERVER 世界王目前造成傷害:"+str(totaldamage))
        dataBase.damageWordBoss(totaldamage)


sched.start()