import argparse
import logging

from dvc.cli import completion
from dvc.cli.command import CmdBaseNoRepo
from dvc.cli.utils import append_doc_link
from dvc.exceptions import DvcException
from dvc.scm import CloneError

logger = logging.getLogger(__name__)


class CmdGet(CmdBaseNoRepo):
    def _show_url(self):
        from dvc.api import get_url
        from dvc.ui import ui

        try:
            url = get_url(
                self.args.path, repo=self.args.url, rev=self.args.rev
            )
            ui.write(url, force=True)
        except DvcException:
            logger.exception("failed to show URL")
            return 1

        return 0

    def run(self):
        if self.args.show_url:
            return self._show_url()

        return self._get_file_from_repo()

    def _get_file_from_repo(self):
        from dvc.repo import Repo

        try:
            Repo.get(
                self.args.url,
                path=self.args.path,
                out=self.args.out,
                rev=self.args.rev,
                jobs=self.args.jobs,
            )
            return 0
        except CloneError:
            logger.exception("failed to get '%s'", self.args.path)
            return 1
        except DvcException:
            logger.exception(
                "failed to get '%s' from '%s'", self.args.path, self.args.url
            )
            return 1


def add_parser(subparsers, parent_parser):
    GET_HELP = "Download file or directory tracked by DVC or by Git."
    get_parser = subparsers.add_parser(
        "get",
        parents=[parent_parser],
        description=append_doc_link(GET_HELP, "get"),
        help=GET_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    get_parser.add_argument(
        "url", help="Location of DVC or Git repository to download from"
    )
    get_parser.add_argument(
        "path", help="Path to a file or directory within the repository"
    ).complete = completion.FILE
    get_parser.add_argument(
        "-o",
        "--out",
        nargs="?",
        help="Destination path to download files to",
        metavar="<path>",
    ).complete = completion.DIR
    get_parser.add_argument(
        "--rev",
        nargs="?",
        help="Git revision (e.g. SHA, branch, tag)",
        metavar="<commit>",
    )
    get_parser.add_argument(
        "--show-url",
        action="store_true",
        help="Print the storage location (URL) the target data would be "
        "downloaded from, and exit.",
    )
    get_parser.add_argument(
        "-j",
        "--jobs",
        type=int,
        help=(
            "Number of jobs to run simultaneously. "
            "The default value is 4 * cpu_count(). "
        ),
        metavar="<number>",
    )
    get_parser.set_defaults(func=CmdGet)
