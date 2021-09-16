from typing import List
from pdpyras import APISession


class PD(object):

    session = None
    cfg = None

    def __init__(self, cfg: dict) -> None:
        super().__init__()
        if not self.session:
            self.cfg = cfg
            self.session = APISession(cfg["apikey"], default_from=cfg["email"])

    def list_incidents(
        self, userid: list = None, statuses: list = ["triggered", "acknowledged"], urgencies: list = ["high", "low"]
    ):
        params = {"statuses[]": statuses, "urgencies[]": urgencies}
        if userid:
            params["user_ids[]"] = userid

        incs = self.session.list_all("incidents", params=params)

        return incs

    def list_my_incidents(self, statuses: list = ["triggered", "acknowledged"], urgencies: list = ["high", "low"]):
        return self.list_incidents([self.cfg["uid"]], statuses, urgencies)

    def get_user_names(self, incident: dict) -> List[str]:

        assignments = incident["assignments"]

        users = list()
        for a in assignments:
            users.append(a["assignee"]["summary"])

        return users

    def get_incident(self, id: str) -> dict:
        r = self.session.rget(f"/incidents/{id}")
        if r:
            return r

    def ack(self, inc):
        if inc["status"] != "acknowledged":
            inc["status"] = "acknowledged"
        return inc

    def resolve(self, i):
        if i["status"] == "acknowledged":
            i["status"] = "resolved"
        return i

    def snooze(self, i, duration=14400):
        if i["status"] == "acknowledged":
            self.session.post(f"/incidents/{i['id']}/snooze", json={"duration": duration})
        return i

    def update_incident(self, inc):
        return self.session.rput(f"/incidents/{inc['id']}", json=inc)

    def bulk_update_incident(self, incs):
        return self.session.rput("incidents", json=incs)
