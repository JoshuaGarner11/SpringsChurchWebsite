# Offline test of the CCB sanitizer with fake XML (no network, no credentials). Run: python3 scripts/test_ccb_sync.py scripts/ccb_sync.py
import sys, json, importlib.util, xml.etree.ElementTree as ET
spec = importlib.util.spec_from_file_location("s", sys.argv[1]); s = importlib.util.module_from_spec(spec); spec.loader.exec_module(s)
cal = ET.fromstring("""<ccb_api><response><items>
<item><date>2026-12-05</date><event_name ccb_id="11">Springs Men | Breakfast Gathering</event_name><event_description>Meet at 4410 Example Ridge Dr first. Join us! Questions? bob.smith@gmail.com or (719) 555-1234 or info@springs.church, (719) 488-8331</event_description><start_time>08:00:00</start_time><end_time>09:30:00</end_time><event_type>Event</event_type><location>Kids' Auditorium, 1515 Auto Mall Loop, Colorado Springs, CO</location><group_name>Springs Men</group_name><group_type>Men</group_type><grouping_name>Adults</grouping_name><leader_name>Leader Person</leader_name><leader_phone>(719) 555-0000</leader_phone><leader_email>leader@example.com</leader_email></item>
<item><date>2026-12-06</date><event_name ccb_id="12">Smith | Home Group</event_name><start_time>18:30:00</start_time><end_time>20:00:00</end_time><location>Smith Residence, 123 Any St, Colorado Springs</location><group_name>Smith</group_name><group_type>Home Group</group_type></item>
<item><date>2026-12-07</date><event_name ccb_id="13">Women's Study</event_name><start_time>09:30:00</start_time><end_time>11:00:00</end_time><location>6910 Example Drive</location><group_name>Women</group_name><group_type>Women</group_type></item>
<item><date>2027-01-15</date><event_name ccb_id="14">Youth | Winter Retreat</event_name><start_time>17:00:00</start_time><end_time>23:59:00</end_time><location>Camp Elim, 1234 Mountain Rd, Woodland Park, CO</location><group_name>Youth</group_name></item>
</items></response></ccb_api>""")
grp = ET.fromstring("""<ccb_api><response><items>
<item><id>9</id><name>**Tuesday Men's Study**</name><group_type_name>Men</group_type_name><grouping_name>Adults</grouping_name><area_name ccb_id="2">North</area_name><meet_day_name>Tuesday</meet_day_name><meet_time_name>Evening</meet_time_name><description>Bring a Bible. Text Joe 719-555-7777</description><membership_type>Open</membership_type><owner_name>Joe Leader</owner_name><owner_email_primary>joe@example.com</owner_email_primary></item>
<item><id>10</id><name>Anthem Small Group</name><group_type_name>Student</group_type_name><grouping_name>Youth</grouping_name></item>
</items></response></ccb_api>""")
st = {k: 0 for k in ("kept","dropped_home","dropped_bad_date","groups_kept","groups_dropped_kids_youth")}
ev = s.build_events(cal, st); gr = s.build_groups(grp, st)
blob = json.dumps({"ev": ev, "gr": gr})
for bad in ["bob.smith", "555-1234", "Leader Person", "leader@example", "Residence", "123 Any", "6910", "1234 Mountain", "joe@example", "555-7777", "Joe Leader", "Anthem"]:
    assert bad not in blob, "LEAKED: " + bad
assert [e["title"] for e in ev] == ["Springs Men | Breakfast Gathering", "Youth | Winter Retreat"], [e["title"] for e in ev]
assert ev[0]["venue"] == "Kids' Auditorium" and ev[0]["onCampus"] and ev[0]["start"] == "2026-12-05T08:00:00-07:00", ev[0]
assert "info@springs.church" in ev[0]["desc"] and "488-8331" in ev[0]["desc"], ev[0]["desc"]
assert ev[1]["venue"] == "Camp Elim" and not ev[1]["onCampus"], ev[1]
assert [g["name"] for g in gr] == ["Tuesday Men's Study"] and gr[0]["area"] == "North", gr
assert "4410" not in blob and not s.leak_check([ev, gr]), s.leak_check([ev, gr])
print("sanitizer OK", st)
