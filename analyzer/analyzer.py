from analyzer.utils.scrot import *
from analyzer.utils.UIED import invoke_UIED
from analyzer.utils.clustering import cluster
from analyzer.utils.gemini import *
import analyzer.utils.xorg as xorg

# user_tasks = [
#     "writing code",
#     # "listen to music",
#     # "research for upcoming project about shoes",
#     # "practice programming in general"
# ]

# tmp_clusters = [
# ['Black Friday Week', 'Epic deals', 'all week long'],
# ['Top 100 deals', 'Black Friday', '43 % off', 'Black Friday', 'Deal'],
# ['Buzzworthy deals', '35 % off', 'Black Friday', 'Deal'],
# ["nd were trying to get a shower in before it's too late in the the house", 'oing home and getting a shower', 'Black Friday do that instead', 'Deal', 'Frame', 'Skylight', 'Buzzworthy deals', 'Black Friday', '40 % off'],
# ['Amazon Devices deals', '63 % off', 'Black Friday', 'Deal'],
# ['20 % off', 'Black Friday', 'Deal', '62 % off', 'Black Friday', 'Deal', '43 % off'],
# ['Black Friday do that instead', 'Deal', 'Frame', 'Skylight', 'Black Friday', 'Deal', '40 % off', 'Black Friday', '25 % off', 'www.amazon.ca/blackfriday/?_encoding=UTF8&pd_rd_w=5xg3n&c...8900d6-ec5e-4812-9b6c-8f5862553885&ref_=pd_hp_d_hero_unk'],
# ['63 % off', 'Black Friday', 'Deal', '50 % off', 'Black Friday', 'Deal']
# ]

def analyze(tasks: list[str]):
    # 0. fetch currently active windows
    current_windows = xorg.get_current_windows()
    stacking_list = xorg.get_stacking_list()
    # print(current_windows)
    # print(stacking_list)
    # 1. UIED on scrot
    scrot_file = scrot()
    xorg.notify("Simon says freeze!",
                f"Simon might be slow, but you can't run from Simon forever...")
    invoke_UIED(scrot_file)
    # 2. cluster image elements
    clusters = cluster()
    clusters_text = []
    for c in clusters:
        clusters_text.append([ txt["content"] for txt in c["texts"] ])
    # 3. Pass to gemini
    #   3.5. determine which windows to kill
    prompt = build_gemini_prompt(tasks, [ "\n".join(txt) for txt in clusters_text ])
    kill_list = parse_gemini_results(gemini_query(prompt))
    # print(kill_list)

    kill_clusters = [ c for c, kill in zip(clusters, kill_list) if kill]
    print(kill_clusters)
    # 4. kill windows
    kill_pos = [
        (round((c["column_max"] + c["column_min"]) / 2), round((c["row_max"] + c["row_min"]) / 2))
        for c in kill_clusters
    ]

    pids_to_kill = set()
    for x, y in kill_pos:
        pids = xorg.get_window_at_coords(x, y, current_windows, stacking_list)
        if pids:
            pids_to_kill.add(pids)
        else:
            print(f"Warn: ignoring {x}, {y} because bad coordinates")

    if not pids_to_kill:
        xorg.notify("Simon says, Carry on B^)",
                    f"Good job! Simon didn't find anything funny.")
    for hex, pid in pids_to_kill:
        xorg.notify("Simon catches you red-handed!",
                    f"Killing {xorg.get_window_title(hex)}!")
        subprocess.run(['kill', str(pid)])
        xorg.toggle_wallpaper()
        xorg.simon_disappoint()

    # 5. change wallpaper briefly

# analyze()
