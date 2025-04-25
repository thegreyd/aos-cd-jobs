node() {
    wrap([$class: "BuildUser"]) {
        // gomod created files have filemode 444. It will lead to a permission denied error in the next build.
        sh "chmod u+w -R ."
        checkout scm
        def buildlib = load("pipeline-scripts/buildlib.groovy")
        def commonlib = buildlib.commonlib

        commonlib.describeJob("prepare-release-konflux", """
            <h2>Prepare an OCP release to release via Konflux</h2>
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
                            name: "SHIPMENT_REPO_URL",
                            description: "(Optional) URL of the shipment repo to use instead of the default one",
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
            currentBuild.displayName += " ${params.BUILD_VERSION} - ${params.ASSEMBLY}"
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
                    "prepare-release-konflux",
                    "--group", "openshift-${params.BUILD_VERSION}",
                    "--assembly", params.ASSEMBLY,
                ]
                if (params.SHIPMENT_REPO_URL) {
                    cmd += ["--shipment-data-path", params.SHIPMENT_REPO_URL]
                }
                echo "Will run ${cmd}"
                
                withCredentials([
                    string(credentialsId: 'art-bot-slack-token', variable: 'SLACK_BOT_TOKEN'),
                ]) {
                    commonlib.shell(script: cmd.join(' '))
                }
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
