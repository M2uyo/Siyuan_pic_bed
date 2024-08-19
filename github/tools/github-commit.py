from collections import defaultdict

import requests

from github.tools.github_token import github_token


class GithubCommitControl:
    repo_owner = 'M2uyo'  # 替换为实际的GitHub用户名
    repo_name = 'Siyuan_pic_bed'  # 替换为实际的仓库名
    branch_name = 'dev'  # 指定要获取提交记录的分支名
    token = github_token  # 替换为你的GitHub token
    stop_hash = '77afa45c02f300fd52d0a36bc2c659eb2a68f6b3'

    sort_key = ["fix", "feat", "perf", "optimize", "refactor", "style", "del", "log"]

    ignore_key = ["changelog", "release", "build", "", "ignore", "readme", "config"]

    def __init__(self):
        self.commits = []
        self.commit_info = []
        self.get_commits_on_branch()

    def get_commits_on_branch(self):
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/commits?sha={self.branch_name}"
        headers = {
            "Authorization": f"token {self.token}"
        }
        while url:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            for commit in response.json():
                if commit['sha'] == self.stop_hash:
                    return  # 找到指定的hash值，返回当前列表并停止遍历
                # 将提交记录添加到列表中
                self.commits.append(commit)
                # 检查当前提交的hash值是否是我们要停止的hash值

            # 检查是否有下一页的链接
            if 'next' in response.links:
                url = response.links['next']['url']
            else:
                break

    def extract_commit_info(self):
        commit_info = []
        for commit in self.commits:
            message = commit['commit']['message']
            html_url = commit['html_url']
            commit_info.append((message, html_url))
        return commit_info

    def show(self):
        for message, link in self.commit_info:
            print(f"Message: {message}\nLink: {link}\n")

    def convert_to_change_log(self):
        info = defaultdict(list)
        for commit in self.commits:
            message = commit['commit']['message']
            log_split = message.split(":")
            key, message = log_split[0], ":".join(log_split[1:]).strip()
            message = f"[{message}]({commit['html_url']})"

            if key in self.ignore_key:
                continue
            info[key].append(message)
        return info

    def output_changelog(self):
        change_log = self.convert_to_change_log()
        for key, value in sorted(change_log.items(), key=lambda x: self.sort_key.index(x[0])):
            print(f"\n#### {key}\n")
            for msg in value:
                print(f'- {msg}')


if __name__ == '__main__':
    ctl = GithubCommitControl()
    ctl.output_changelog()
