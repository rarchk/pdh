#
# This file is part of the pdh (https://github.com/mbovo/pdh).
# Copyright (c) 2020-2023 Manuel Bovo.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
from typing import Any
from .pd import URGENCY_HIGH
from datetime import datetime
from rich.pretty import pretty_repr
import re
from .filters import Filter


class Transformation(object):
    """
    Transformation is a collection of methods to transform dictionaries
    """

    def identity(field_name):
        def fun(i: dict) -> Any:
            return i[field_name]

        return fun

    def extract_date(item_name: str, format: str = "%Y-%m-%dT%H:%M:%SZ"):
        def extract(i: dict) -> str:
            d = datetime.strptime(i[item_name], format)
            duration = datetime.utcnow() - d
            data = {}
            data["d"], remaining = divmod(duration.total_seconds(), 86_400)
            data["h"], remaining = divmod(remaining, 3_600)
            data["m"], _ = divmod(remaining, 60)

            time_parts = [f"{round(value)}{name}" for name, value in data.items() if value > 0]
            if time_parts:
                return " ".join(time_parts) + " ago"
            else:
                return "less than 1m ago"

        return extract

    def extract_field(
        item_name: str,
        colors: list = ["red", "cyan"],
        check_field: str = "urgency",
        check_value: str = URGENCY_HIGH,
        check: bool = False,
        change_dict: dict = None,
    ):
        def extract(i: dict) -> str:
            item = i[item_name]
            if change_dict is not None:
                if i[item_name] in change_dict.keys():
                    item = change_dict[i[item_name]]
            if check:
                if i[check_field] == check_value:
                    if item[0] != "[":
                        item = f"{item}".replace("[", "\\[")  # escape [ and ] to avoid rich formatting
                    return f"[{colors[0]}]{item}[/{colors[0]}]"
                return f"[{colors[1]}]{item}[/{colors[1]}]"
            else:
                return f"{item}"

        return extract

    def extract_assignees(color: str = "magenta") -> str:
        def extract(i: dict) -> str:
            return f'[{color}]{", ".join([a["assignee"]["summary"] for a in i["assignments"]])}[/{color}]'

        return extract

    def extract_alerts(field_name, alert_fields: list[str] = ["id", "summary", "created_at", "status"]):
        def extract(i: dict) -> str:
            # print(i)
            # print(field_name, alert_fields)
            alerts = i[field_name]
            ret = dict()
            for alert in alerts:
                alert_obj = dict()
                # print("alert:", alert)
                for field in alert_fields:
                    if field not in alert:
                        # processing a field in a way body.details.dashobard_url
                        alert_obj[field] = Transformation.extract_nested_field(field)
                    else:
                        alert_obj[field] = Transformation.extract_field(field, check=False)
                        # alert_obj[field] = alert[field]
                # alert_obj['alert_id'] = f"[link={alert['html_url']}]{alert['id']}[/link]"
                alert_obj['id'] = Transformation.ref_links('id', 'html_url')
                # print(alert_obj, type(alert_obj))
                filtered = Filter.do(alerts, alert_obj, [])
                if 'body.details.dashboard_url' in alert_fields:
                    for idx,_ in enumerate(filtered):
                        filtered[idx]['dashboard'] = Transformation.str_to_html(filtered[idx]['body.details.dashboard_url'])
                        filtered[idx].pop("body.details.dashboard_url")

                if 'body.details.runbook_url' in alert_fields:
                    for idx,_ in enumerate(filtered):
                        filtered[idx]['runbook'] = Transformation.str_to_html(filtered[idx]['body.details.runbook_url'])
                        filtered[idx].pop("body.details.runbook_url")

                ret = filtered
            return pretty_repr(ret)
            # return yaml.dump(ret)

        return extract

    def extract_pending_actions():
        return lambda i: str([f"{a['type']} at {a['at']}" for a in i["pending_actions"]])

    def extract_users_teams():
        return lambda x: ",".join([t["summary"] for t in x["teams"]])

    def extract_nested_field(field: str,):
        from jsonpath_ng import parse
        expression = parse(field)
        # alert_obj.update({field: match.value for match in expression.find(alert)})
        return lambda x: (match.value for match in expression.find(x))

    def ref_links(ref_field: str, link_field: str):
        return lambda x: f"[link={x[link_field]}]{x[ref_field]}[/link]"

    def str_to_html(field: str):
        links = re.findall(r'(https?://\S+)', field)
        link_str = ""
        for _, link in enumerate(links):
            link_str+=f"[link={link}]{link}[/link]\n"
        return link_str
