#!/usr/bin/env python
"""Run `python script_name.py -h` for info.

WARNING: Save a backup of your code base before running this!
"""
import argparse
import re
import sys
from pathlib import Path
from typing import Callable, Sequence, Pattern, Tuple

CALLBACK_TRANSITION_PATTERN = re.compile(
    r"(?<!async )def (\w+)\((update|_)(: (telegram\.|)Update|), (context|_)(:"
    r" (telegram\.ext\.|)CallbackContext|)\)"
)
JOB_TRANSITION_PATTERN = re.compile(
    r"(?<!async )def (\w+)\((context|_)(: (telegram\.ext\.|)CallbackContext|)\)"
)


def callback_signature_transition(_: Path, contents: str) -> str:
    contents = re.sub(
        CALLBACK_TRANSITION_PATTERN,
        r"async def \1(\2\3, \5: \7ContextTypes.DEFAULT_TYPE)",
        contents,
    )
    contents = re.sub(
        JOB_TRANSITION_PATTERN,
        r"async def \1(\2: \4ContextTypes.DEFAULT_TYPE)",
        contents,
    )
    # this line is for users transitioning from v20.0a0 to 20.0a1
    return contents.replace("CallbackContext.DEFAULT_TYPE", "ContextTypes.DEFAULT_TYPE")


AWAIT_BOT_METHODS_PATTERNS: Sequence[Tuple[Pattern, str]] = [
    (re.compile(r"(?<!await) (\w+\.|)bot\.([\w\.]+)\("), r" await \1bot.\2("),
    (
        re.compile(
            r"(?<!await) (message|update|callback_query|inline_query|query)\.([\w\.]+)\("
        ),
        r" await \1.\2(",
    ),
]


def await_bot_methods_transition(_: Path, contents: str) -> str:
    for pattern, replace in AWAIT_BOT_METHODS_PATTERNS:
        contents = re.sub(pattern, replace, contents)
    return contents


RUN_ASYNC_PATTERNS = [
    (re.compile(r"run_async=True"), "block=False"),
    (re.compile(r"run_async=False"), "block=True"),
]


def run_async_transition(_: Path, contents: str) -> str:
    for pattern, replace in RUN_ASYNC_PATTERNS:
        contents = re.sub(pattern, replace, contents)
    return contents


def init_transition(_: Path, contents: str) -> str:
    return re.sub(
        r"Updater\((token=|)([\w\d:\'\"\[\]\.\(\)\s]+)\)",
        r"Application.builder().token(\2).build()",
        contents,
    )


def updater_transition(_: Path, contents: str) -> str:
    return re.sub(
        r"updater\.start_(polling|webhook)\(", r"application.run_\1(", contents
    )


def dispatcher_transition(_: Path, contents: str) -> str:
    return contents.replace("dispatcher", "application")


def run_async_decorator_transition(_: Path, contents: str) -> str:
    return contents.replace("@run_async\n", "")


def use_context_transition(_: Path, contents: str) -> str:
    contents = re.sub(r"use_context=(True|False)(,|\n)", "", contents)
    return re.sub(r"use_context=(True|False)\)", ")", contents)


def filters_transition(_: Path, contents: str) -> str:
    # Order of the replacements matters!
    # Filters.text -> Filters.TEXT
    contents = re.sub(
        r"Filters\.(\w+)([ ~&\^,\)])",
        lambda match: f"filters.{match.group(1).upper()}{match.group(2)}",
        contents,
    )
    # Filters.chat(…) -> filters.Chat(…)
    contents = re.sub(
        r"Filters\.(\w)(\w+)\(",
        lambda match: f"filters.{match.group(1).upper()}{match.group(2)}(",
        contents,
    )
    # Filters.status_update.new_chat_member -> filters.StatusUpdate.new_chat_member
    contents = re.sub(
        r"Filters\.([\w_]+)\.",
        lambda match: f"filters.{''.join(word.title() for word in match.group(1).split('_'))}.",
        contents,
    )
    # Filters.Dice.darts(…) -> filters.Dice.Darts(…)
    contents = re.sub(
        r"filters\.([\w]+)\.([\w_]+)\(",
        lambda match: (
            f"filters.{match.group(1)}.{''.join(word.title() for word in match.group(2).split('_'))}("
        ),
        contents,
    )
    # filters.StatusUpdate.new_chat_member -> filters.StatusUpdate.NEW_CHAT_MEMBER
    contents = re.sub(
        r"filters\.([\w]+)\.([\w_]+)([ ~&\^,\)])",
        lambda match: f"filters.{match.group(1)}.{match.group(2).upper()}{match.group(3)}",
        contents,
    )
    return contents


def job_pass_data_transition(_: Path, contents: str) -> str:
    return re.sub(
        r"context=context.(user|chat)_data", r"\1_id=update.effective_\1.id", contents
    )


def job_context_to_data_rename_transition(_: Path, contents: str) -> str:
    contents = re.sub(
        r"run_(\w+)\(([\w,].*)?(context=)(\w+)([\w,].*)\)",
        r"run_\1\(\2data=\4\5\)",
        contents,
    )
    return contents.replace("context.job.context", "context.job.data")


def video_chat_transiton(_: Path, contents: str) -> str:
    return (
        contents.replace("voice_chat", "video_chat")
        .replace("VoiceChat", "VideoChat")
        .replace("VOICE_CHAT", "VIDEO_CHAT")
    )


def updater_start_arguments_transition(_: Path, contents: str) -> str:
    return (
        contents.replace("clean=True", "drop_pending_updates=True")
        .replace("force_event_loop=True,", "")
        .replace("force_event_loop=True),", ")")
    )


def renamed_bot_methods_transition(_: Path, contents: str) -> str:
    return (
        contents.replace("kick_chat_member", "ban_chat_member")
        .replace("kickChatMember", "banChatMember")
        .replace("kick_member", "ban_member")
        .replace("get_chat_members_count", "get_chat_member_count")
        .replace("getChatMembersCount", "getChatMemberCount")
        .replace("get_members_count", "get_member_count")
    )


def rename_handler_to_base_handler(_: Path, contents: str) -> str:
    return re.sub(
        r"(class \w+)\((telegram\.ext\.|)Handler\)", r"\1\(\2BaseHandler)\)", contents
    )


TRANSITIONS: Sequence[Callable[[Path, str], str]] = [
    callback_signature_transition,
    await_bot_methods_transition,
    run_async_transition,
    use_context_transition,  # place before init_transition
    init_transition,
    updater_transition,
    dispatcher_transition,
    run_async_decorator_transition,
    filters_transition,
    job_pass_data_transition,
    job_context_to_data_rename_transition,  # place after job_pass_data_transition
    video_chat_transiton,
    updater_start_arguments_transition,
    renamed_bot_methods_transition,
    rename_handler_to_base_handler,
]


def transition_file(file: Path) -> None:
    file_contents = file.read_text(encoding="utf8")

    for transition in TRANSITIONS:
        file_contents = transition(file, file_contents)

    file.write_text(file_contents, encoding="utf8")


def run_transition(files: Sequence[str], recurse: bool) -> None:
    for file in files:
        path = Path(file)
        if path.is_dir():
            if recurse:
                for file_path in path.rglob("*.py"):
                    transition_file(file_path)
        else:
            transition_file(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Helper script ease transition to PTB v20. Manual work will still be required! "
            "This script will likely produce some false transitions. "
            "If you encounter import errors, try passing the files one by one. "
            "Example usage: `python script_name.py path/to/file.py path/to/directory -r`."
        )
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Use to specify the names of the files or directories that should be transitioned. ",
    )
    parser.add_argument(
        "-r",
        "--recurse",
        default=False,
        dest="recurse",
        action="store_true",
        help="Whether to recurse through directories searching for Python files.",
    )

    args = parser.parse_args()
    sys.exit(run_transition(files=args.files, recurse=args.recurse))
