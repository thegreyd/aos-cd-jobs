node() {
    wrap([$class: "BuildUser"]) {
        // gomod created files have filemode 444. It will lead to a permission denied error in the next build.
        sh "chmod u+w -R ."
        checkout scm
        def buildlib = load("pipeline-scripts/buildlib.groovy")
        def commonlib = buildlib.commonlib

        commonlib.describeJob("konflux-release", """
            <h2>Create a Konflux Release from a Shipment config</h2>
        """)

        properties(
            [
                disableResume(),
                buildDiscarder(
                    logRotator(
                        artifactDaysToKeepStr: "30",
                        artifactNumToKeepStr: "",
                        daysToKeepStr: "30",
                        numToKeepStr: "")),
                [
                    $class: "ParametersDefinitionProperty",
                    parameterDefinitions: [
                        commonlib.ocpVersionParam('BUILD_VERSION', '4'),
                        commonlib.artToolsParam(),
                        string(
                            name: "ASSEMBLY",
                            description: "The name of the associated assembly",
                            defaultValue: "test",
                            trim: true
                        ),
                        string(
                            name: "APPLICATION",
                            description: "The name of the associated Konflux application",
                            defaultValue: "test",
                            trim: true
                        ),
                        string(
                            name: "ADVISORY_KEY",
                            description: "Name of the advisory template to use for shipment",
                            defaultValue: "",
                            trim: true
                        ),
                        commonlib.mockParam(),
                    ]
                ],
            ]
        )

        commonlib.checkMock()
        stage("initialize") {
            currentBuild.displayName += " ${params.BUILD_VERSION} - ${params.ASSEMBLY} - ${params.APPLICATION}"
        }
        try {
            stage("build") {
                buildlib.cleanWorkdir("./artcd_working")
                sh "mkdir -p ./artcd_working"
                def cmd = [
                    "artcd",
                    "-vv",
                    "--working-dir=./artcd_working",
                    "--config", "./config/artcd.toml",
                ]

                cmd += [
                    "prepare-shipment",
                    "--group", "openshift-${params.BUILD_VERSION}",
                    "--assembly", params.ASSEMBLY,
                    "--application", params.APPLICATION,
                ]
                if (params.ADVISORY_KEY) {
                    cmd << "--advisory-key=${params.ADVISORY_KEY}"
                }
                echo "Will run ${cmd}"
                commonlib.shell(script: cmd.join(' '))
            }
        } finally {
            stage("save artifacts") {
                commonlib.safeArchiveArtifacts([
                    "artcd_working/email/**",
                    "artcd_working/**/*.json",
                    "artcd_working/**/*.log",
                ])
            }
        }
    }
}
