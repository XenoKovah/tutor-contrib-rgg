Raccoon Gang Gamification plugin for `Tutor <https://docs.tutor.edly.io>`__
#####################################################

RGG is a plugin for Tutor that adds gamification features to Open edX platform.


Installation
************

.. code-block:: bash

    pip install git+https://gitlab.raccoongang.com/owlox-team/productsforge/oex/tutor-contrib-rgg

Configuration
*************

Current RG Tutor deployment requires the following configuration:

.. code-block:: yaml

    TUTOR_RGG_HOST: "{% if 'rgg' in TUTOR_PLUGINS %}gamma.{{ TUTOR_LMS_HOST }}{% else %}{% endif %}"
    TUTOR_RGG_DOCKER_IMAGE: "{{ DOCKER_REGISTRY }}/rgg:{{ RELEASE_VERSION }}"
    TUTOR_RGG_MYSQL_PASSWORD: "{{ VAULT_RGG_MYSQL_PASSWORD }}"
    TUTOR_RGG_DEFAULT_APP_KEY: "{{ VAULT_RGG_DEFAULT_APP_KEY }}"
    TUTOR_RGG_DEFAULT_APP_SECRET: "{{ VAULT_RGG_DEFAULT_APP_SECRET }}"
    TUTOR_RGG_DJANGO_ADMIN_PASS: "{{ VAULT_RGG_DJANGO_ADMIN_PASS }}"


Usage
*****

1. Create GitLab CI access token with the following scopes (read_repository, read_registry): https://gitlab.raccoongang.com/-/user_settings/personal_access_tokens
2. Configure the token in the `config.yml` file:

.. code-block:: bash

    tutor config save --set CI_JOB_TOKEN=your_token

3. Enable and build images

.. code-block:: bash

    tutor plugins enable rgg
    tutor images build openedx
    tutor images build rgg
    tutor images build rgg-dev
    tutor images build mfe

4. Start the platform

.. code-block:: bash

    tutor local launch

License
*******

This software is licensed under the terms of the AGPLv3.
