Continuous integration
######################

Pygount can produce output that can be processed by the
`SLOCCount plug-in <https://wiki.jenkins-ci.org/display/JENKINS/SLOCCount+Plugin>`_
for the `Jenkins <https://jenkins.io/>`_ continuous integration server.

It's recommended to run pygount as one of the first steps in your build
process before any undesired file like compiler targets or generated source
code are built.

An example "Execute shell" build step for Jenkins is:

.. code-block:: bash

    $ pygount --format=cloc-xml --out cloc.xml --suffix=py --verbose

Then add a post-build action "Publish SLOCCount analysis results" and set
"SLOCCount report" to "cloc.xml".
