from __future__ import annotations

import os
import typing as t
from glob import glob

import importlib_resources
from tutor import hooks
from tutor.config import load
from tutormfe.hooks import PLUGIN_SLOTS

from .__about__ import __version__


def is_plugin_loaded(plugin_name: str) -> bool:
    """
    Check if the provided plugin is loaded.
    """

    return plugin_name in hooks.Filters.PLUGINS_LOADED.iterate()

########################################
# CONFIGURATION
########################################

hooks.Filters.CONFIG_DEFAULTS.add_items(
    [
        # Add your new settings that have default values here.
        # Each new setting is a pair: (setting_name, default_value).
        # Prefix your setting names with 'RGG_'.
        ("RGG_VERSION", __version__),
        ("RGG_DOCKER_IMAGE", "{{ DOCKER_REGISTRY }}raccoongang/rgg:{{ RGG_VERSION }}"),
        ("RGG_DOCKER_IMAGE_DEV", "{{ DOCKER_REGISTRY }}raccoongang/rgg-dev:{{ RGG_VERSION }}"),
        ("RGG_HOST", "gamma.{{ LMS_HOST }}"),
        ("RGG_MYSQL_DATABASE", "rgg"),
        ("RGG_REDIS_DB", "3"),
        ("RGG_DJANGO_ADMIN_USER", "admin"),
        ("RGG_DJANGO_ADMIN_EMAIL", "admin@mail.com"),
        ("RGG_AWS_STORAGE_BUCKET_NAME", "rgg"),
        ("RGG_AWS_S3_REGION_NAME", "eu-central-1"),
        ("RGG_AWS_DEFAULT_ACL", "None"),
        ("RGG_DEFAULT_FILE_STORAGE", "storages.backends.s3boto3.S3Boto3Storage"),
        ("RGG_REPOSITORY", "https://gitlab.raccoongang.com/foss/rgg/gamma.git"),
        ("RGG_REPOSITORY_VERSION", "nau"),
        ("RGG_BRIDGE_REPOSITORY", "https://gitlab.raccoongang.com/foss/rgg/edx-gamma-bridge.git"),
        ("RGG_BRIDGE_REPOSITORY_VERSION", "release/teak"),
        ("RGG_DASHBOARD_REPOSITORY", "https://gitlab.raccoongang.com/foss/rgg/edx-gamma-dashboard.git"),
        ("RGG_DASHBOARD_REPOSITORY_VERSION", "nau"),
        ("RGG_WIDGETS_REPOSITORY", "https://gitlab.raccoongang.com/foss/rgg/frontend-rgg-widgets.git"),
        ("RGG_WIDGETS_VERSION", "main"),
        ("RGG_OAUTH2_KEY_SSO", "rgg-key-sso"),
        ("RGG_OAUTH2_KEY_SSO_DEV", "rgg-key-sso-dev"),
        ("RGG_GAMMA_SETTINGS_URL", "{{ ('https' if ENABLE_HTTPS else 'http') ~ '://' ~ (RGG_HOST if ENABLE_HTTPS else 'localhost:9700') ~ '/gamma/badges/' }}"),
        ("RGG_DEFAULT_FILE_STORAGE_OPTIONS", {}),
    ]
)

hooks.Filters.ENV_TEMPLATE_VARIABLES.add_items(
    [
        ("is_plugin_loaded", is_plugin_loaded),
    ],
)

hooks.Filters.CONFIG_UNIQUE.add_items(
    [
        # Add settings that don't have a reasonable default for all users here.
        # For instance: passwords, secret keys, etc.
        # Each new setting is a pair: (setting_name, unique_generated_value).
        # Prefix your setting names with 'RGG_'.
        # For example:
        ### ("RGG_SECRET_KEY", "{{ 24|random_string }}"),
        ("RGG_MYSQL_USERNAME", "rgg"),
        ("RGG_MYSQL_PASSWORD", "{{ 24|random_string }}"),
        ("RGG_DEFAULT_APP_KEY", "{{ 24|random_string }}"),
        ("RGG_DEFAULT_APP_SECRET", "{{ 24|random_string }}"),
        ("RGG_DJANGO_ADMIN_PASS", "{{ 24|random_string }}"),
        ("EDX_API_KEY", "{{ 24|random_string }}"),
        ("RGG_OAUTH2_SECRET", "{{ 24|random_string }}"),
    ]
)

# Inject settings for file storage options which can be extended via `config.yml`.
@hooks.Actions.PROJECT_ROOT_READY.add()
def _extend_with_file_storage_settings(root: str) -> None:
    current_config = load(root)

    file_storage_backend = current_config.get("RGG_DEFAULT_FILE_STORAGE")
    file_storage_options = current_config.get("RGG_DEFAULT_FILE_STORAGE_OPTIONS") or {}

    patch_settings_str = []

    # Override the DEFAULT_FILE_STORAGE setting.
    if file_storage_backend:
        patch_settings_str.append(f"DEFAULT_FILE_STORAGE = '{file_storage_backend}'")

    # Extend file storage backend with options.
    for key, value in file_storage_options.items():
        patch_settings_str.append(f"{key} = {repr(value)}")

    # Inject into rgg-common-settings.
    joined_settings_str = "\n".join(patch_settings_str)
    hooks.Filters.ENV_PATCHES.add_items([("rgg-common-settings", joined_settings_str)])

hooks.Filters.CONFIG_OVERRIDES.add_items(
    [
        # Danger zone!
        # Add values to override settings from Tutor core or other plugins here.
        # Each override is a pair: (setting_name, new_value). For example:
        ### ("PLATFORM_NAME", "My platform"),
    ]
)


########################################
# INITIALIZATION TASKS
########################################

# To add a custom initialization task, create a bash script template under:
# tutorrgg/templates/rgg/tasks/
# and then add it to the MY_INIT_TASKS list. Each task is in the format:
# ("<service>", ("<path>", "<to>", "<script>", "<template>"))
MY_INIT_TASKS: list[tuple[str, tuple[str, ...]]] = [
    # For example, to add LMS initialization steps, you could add the script template at:
    # tutorrgg/templates/rgg/tasks/lms/init.sh
    # And then add the line:
    ### ("lms", ("rgg", "tasks", "lms", "init.sh")),
    ("lms", ("rgg", "tasks", "lms", "init")),
    ("rgg", ("rgg", "tasks", "mysql", "init")),
    ("rgg", ("rgg", "tasks", "rgg", "init")),
]

if is_plugin_loaded("minio"):
    MY_INIT_TASKS.append(
        ("minio", ("rgg", "tasks", "minio", "init")),
    )


# For each task added to MY_INIT_TASKS, we load the task template
# and add it to the CLI_DO_INIT_TASKS filter, which tells Tutor to
# run it as part of the `init` job.
for service, template_path in MY_INIT_TASKS:
    full_path: str = str(
        importlib_resources.files("tutorrgg")
        / os.path.join("templates", *template_path)
    )
    with open(full_path, encoding="utf-8") as init_task_file:
        init_task: str = init_task_file.read()
    hooks.Filters.CLI_DO_INIT_TASKS.add_item((service, init_task))


########################################
# RG Gamification Public Host
########################################


@hooks.Filters.APP_PUBLIC_HOSTS.add()
def _print_rgg_public_hosts(
    hosts: list[str], context_name: t.Literal["local", "dev"]
) -> list[str]:
    if context_name == "dev":
        hosts += ["{{ RGG_HOST }}:9700"]
    else:
        hosts += ["{{ RGG_HOST }}"]
    return hosts


########################################
# DOCKER IMAGE MANAGEMENT
########################################


# Images to be built by `tutor images build`.
# Each item is a quadruple in the form:
#     ("<tutor_image_name>", ("path", "to", "build", "dir"), "<docker_image_tag>", "<build_args>")
hooks.Filters.IMAGES_BUILD.add_items(
    [
        # To build `myimage` with `tutor images build myimage`,
        # you would add a Dockerfile to templates/rgg/build/myimage,
        # and then write:
        (
            "rgg",
            ("plugins", "rgg", "build", "rgg"),
            "{{ RGG_DOCKER_IMAGE }}",
            (
                "--target=production",
            ),
        ),
        (
            "rgg-dev",
            ("plugins", "rgg", "build", "rgg"),
            "{{ RGG_DOCKER_IMAGE_DEV }}",
            (
                "--target=development",
            ),
        ),
    ]
)

REPO_NAME = "gamma"
APP_NAME = "rgg"

# Automount /rgg/gamma folder from the container
@hooks.Filters.COMPOSE_MOUNTS.add()
def _mount_gamma(
    mounts: list[tuple[str, str]], name: str
) -> list[tuple[str, str]]:
    if name == REPO_NAME:
        mounts.append((APP_NAME, "/rgg/gamma"))
        mounts.append((APP_NAME+"-worker", "/rgg/gamma"))
        mounts.append((APP_NAME+"-beat", "/rgg/gamma"))
    return mounts


# Bind-mount repo at build-time, both for prod and dev images
@hooks.Filters.IMAGES_BUILD_MOUNTS.add()
def _mount_gamma_on_build(
    mounts: list[tuple[str, str]], host_path: str
) -> list[tuple[str, str]]:
    path_basename = os.path.basename(host_path)
    if path_basename == REPO_NAME:
        mounts.append((APP_NAME, f"{APP_NAME}-src"))
        mounts.append((f"{APP_NAME}-dev", f"{APP_NAME}-src"))
    return mounts


# Images to be pulled as part of `tutor images pull`.
# Each item is a pair in the form:
#     ("<tutor_image_name>", "<docker_image_tag>")
hooks.Filters.IMAGES_PULL.add_items(
    [
        # To pull `myimage` with `tutor images pull myimage`, you would write:
        (
            "rgg",
            "{{ RGG_DOCKER_IMAGE }}",
        ),
    ]
)


# Images to be pushed as part of `tutor images push`.
# Each item is a pair in the form:
#     ("<tutor_image_name>", "<docker_image_tag>")
hooks.Filters.IMAGES_PUSH.add_items(
    [
        # To push `myimage` with `tutor images push myimage`, you would write:
        (
            "rgg",
            "{{ RGG_DOCKER_IMAGE }}",
        ),
    ]
)

########################################
# Auto-scaling configuration
########################################
try:
    from tutorrgg.filters import _add_rgg_autoscaling
except ImportError:
    pass


########################################
# TEMPLATE RENDERING
# (It is safe & recommended to leave
#  this section as-is :)
########################################

hooks.Filters.ENV_TEMPLATE_ROOTS.add_items(
    # Root paths for template files, relative to the project root.
    [
        str(importlib_resources.files("tutorrgg") / "templates"),
    ]
)

hooks.Filters.ENV_TEMPLATE_TARGETS.add_items(
    # For each pair (source_path, destination_path):
    # templates at ``source_path`` (relative to your ENV_TEMPLATE_ROOTS) will be
    # rendered to ``source_path/destination_path`` (relative to your Tutor environment).
    # For example, ``tutorrgg/templates/rgg/build``
    # will be rendered to ``$(tutor config printroot)/env/plugins/rgg/build``.
    [
        ("rgg/build", "plugins"),
        ("rgg/apps", "plugins"),
    ],
)


########################################
# PATCH LOADING
# (It is safe & recommended to leave
#  this section as-is :)
########################################

# For each file in tutorrgg/patches,
# apply a patch based on the file's name and contents.
for path in glob(str(importlib_resources.files("tutorrgg") / "patches" / "*")):
    with open(path, encoding="utf-8") as patch_file:
        hooks.Filters.ENV_PATCHES.add_item((os.path.basename(path), patch_file.read()))

########################################
# PLUGIN SLOTS
########################################

RGG_WIDGETS_PKG = "@rgg-plugins/frontend-rgg-widgets@git+{{ RGG_WIDGETS_REPOSITORY }}#{{ RGG_WIDGETS_VERSION }}"
RGG_WIDGET_IMPORT = "const { AvatarProgress, HeaderUserMenuItems, LearningHeaderUserMenuItems } = await import('@rgg-plugins/frontend-rgg-widgets');"

# Note: added `learning` MFE in case when uses general header component (RG theme behavior)
RGG_CORE_MFES = ["account", "discussions", "learner-dashboard", "profile", "learning"]

RGG_HEADER_SECONDARY_MENU_SLOTS = {
    **{mfe: [
        "desktop_secondary_menu_slot", # frontend-component-header <= v6.3.0
        "org.openedx.frontend.layout.header_desktop_secondary_menu.v1", # frontend-component-header >= v6.4.0
    ] for mfe in RGG_CORE_MFES},
}

# Insert widget into Learning MFE when uses learning header component (default Open edX behavior)
RGG_LEARNING_HEADER_SECONDARY_MENU_SLOTS = {
    "learning": [
        "learning_help_slot", # frontend-component-header <= v6.3.0
        "org.openedx.frontend.layout.header_learning_help.v1", # frontend-component-header >= v6.4.0
    ],
}

RGG_HEADER_USER_MENU_SLOTS = {
    **{mfe: [
        "desktop_user_menu_slot", # frontend-component-header <= v6.3.0
        "mobile_user_menu_slot", # frontend-component-header <= v6.3.0
        "org.openedx.frontend.layout.header_desktop_user_menu.v1", # frontend-component-header >= v6.4.0
        "org.openedx.frontend.layout.header_mobile_user_menu.v1", # frontend-component-header >= v6.4.0
    ] for mfe in RGG_CORE_MFES},
}

# Insert widget into Learning MFE when uses learning header component (default Open edX behavior)
RGG_LEARNING_HEADER_USER_MENU_SLOTS = {
    "learning": [
        "learning_user_menu_slot", # frontend-component-header <= v6.3.0
        "org.openedx.frontend.layout.header_learning_user_menu.v1", # frontend-component-header >= v6.4.0
    ],
}

for mfe in RGG_CORE_MFES:
    hooks.Filters.ENV_PATCHES.add_items([
        (f"mfe-dockerfile-post-npm-install-{mfe}", f"RUN npm install {RGG_WIDGETS_PKG}"),
        (f"mfe-env-config-runtime-definitions-{mfe}", RGG_WIDGET_IMPORT),
    ])

# Register plugin slot operations into each (mfe, slot) in `slot_map`.
def register_widgets(slot_map, widget_id_prefix, render_widget, operation="Insert", priority=1, target_widget_id="default_contents"):
    for mfe, slots in slot_map.items():
        for slot in slots:
            widget_id = f"{widget_id_prefix}__{mfe}__{slot}"
            if operation == "Insert":
                plugin_config = f"""
                {{
                    op: PLUGIN_OPERATIONS.Insert,
                    widget: {{
                        id: '{widget_id}',
                        priority: {priority},
                        type: DIRECT_PLUGIN,
                        RenderWidget: {render_widget},
                    }},
                }}"""
            elif operation == "Modify":
                plugin_config = f"""
                {{
                    op: PLUGIN_OPERATIONS.Modify,
                    widgetId: '{target_widget_id}',
                    fn: {render_widget},
                }}"""
            elif operation == "Wrap":
                plugin_config = f"""
                {{
                    op: PLUGIN_OPERATIONS.Wrap,
                    widgetId: '{target_widget_id}',
                    wrapper: {render_widget},
                }}"""
            elif operation == "Hide":
                plugin_config = f"""
                {{
                    op: PLUGIN_OPERATIONS.Hide,
                    widgetId: '{target_widget_id}',
                }}"""
            else:
                raise ValueError(f"Unsupported plugin slot operation: {operation!r}")

            PLUGIN_SLOTS.add_items([(
                mfe,
                slot,
                plugin_config,
            )])


register_widgets(RGG_HEADER_SECONDARY_MENU_SLOTS, "rgg_header_avatar_progress", "AvatarProgress", "Insert")
register_widgets(RGG_LEARNING_HEADER_SECONDARY_MENU_SLOTS, "rgg_learning_header_avatar_progress", "AvatarProgress", "Insert")

register_widgets(RGG_HEADER_USER_MENU_SLOTS, "rgg_header_user_menu_items", "HeaderUserMenuItems", "Modify")
register_widgets(RGG_LEARNING_HEADER_USER_MENU_SLOTS, "rgg_learning_header_user_menu_items", "LearningHeaderUserMenuItems", "Modify")

########################################
# CUSTOM JOBS (a.k.a. "do-commands")
########################################

# A job is a set of tasks, each of which run inside a certain container.
# Jobs are invoked using the `do` command, for example: `tutor local do importdemocourse`.
# A few jobs are built in to Tutor, such as `init` and `createuser`.
# You can also add your own custom jobs:


# To add a custom job, define a Click command that returns a list of tasks,
# where each task is a pair in the form ("<service>", "<shell_command>").
# For example:
### @click.command()
### @click.option("-n", "--name", default="plugin developer")
### def say_hi(name: str) -> list[tuple[str, str]]:
###     """
###     An example job that just prints 'hello' from within both LMS and CMS.
###     """
###     return [
###         ("lms", f"echo 'Hello from LMS, {name}!'"),
###         ("cms", f"echo 'Hello from CMS, {name}!'"),
###     ]


# Then, add the command function to CLI_DO_COMMANDS:
## hooks.Filters.CLI_DO_COMMANDS.add_item(say_hi)

# Now, you can run your job like this:
#   $ tutor local do say-hi --name="Max Sokolski"


#######################################
# CUSTOM CLI COMMANDS
#######################################

# Your plugin can also add custom commands directly to the Tutor CLI.
# These commands are run directly on the user's host computer
# (unlike jobs, which are run in containers).

# To define a command group for your plugin, you would define a Click
# group and then add it to CLI_COMMANDS:


### @click.group()
### def rgg() -> None:
###     pass


### hooks.Filters.CLI_COMMANDS.add_item(rgg)


# Then, you would add subcommands directly to the Click group, for example:


### @rgg.command()
### def example_command() -> None:
###     """
###     This is helptext for an example command.
###     """
###     print("You've run an example command.")


# This would allow you to run:
#   $ tutor rgg example-command
