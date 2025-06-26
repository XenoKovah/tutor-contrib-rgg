Raccoon Gang Gamification plugin for `Tutor <https://docs.tutor.edly.io>`__
#####################################################

RGG is a plugin for Tutor that adds gamification features to Open edX platform.


Installation
************

.. code-block:: bash

    pip install git+https://gitlab.raccoongang.com/foss/rgg/tutor-contrib-rgg.git@teak


Usage
*****

1. Enable and build images

.. code-block:: bash

    tutor plugins enable rgg
    tutor images build openedx
    tutor images build rgg
    tutor images build rgg-dev
    tutor images build mfe

2. Start the platform

.. code-block:: bash

    tutor local launch

3. Local development
.. code-block:: bash

    git clone git@gitlab.raccoongang.com:foss/rgg/gamma.git ./src/gamma
    cd ./src/gamma && git checkout release/teak
    tutor mounts add ./src/gamma
    tutor dev start -d rgg

It's important to note that the cloned repo should have the `gamma` name.

License
*******

This software is licensed under the terms of the AGPLv3.
