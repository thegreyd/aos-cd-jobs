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
                            name: 'RELEASE_ENVIRONMENT',
                            description: '(Required) The environment where release should be created to e.g. stage, prod',
                            defaultValue: '',
                            trim: true
                        ),
                        string(
                            name: 'CONFIG_PATH',
                            description: '(Required) Release config to use',
                            defaultValue: '',
                            trim: true
                        ),
                        string(
                            name: 'SHIPMENT_REPO_URL',
                            description: '(Optional) shipment-data repo to use. To point to a branch/commit use repo@commitish (e.g. https://gitlab.cee.redhat.com/sidsharm/ocp-shipment-data@mybranch). Leave empty for the official repo to be picked.',
                            defaultValue: '',
                            trim: true,
                        ),
                        booleanParam(
                            name: "DRY_RUN",
                            description: "Take no action, just echo what the job would have done.",
                            defaultValue: true
                        ),
                        booleanParam(
                            name: "FORCE",
                            description: "Proceed even if an already existing release/advisory is detected",
                            defaultValue: false
                        ),
                        commonlib.mockParam(),
                    ]
                ],
            ]
        )

        commonlib.checkMock()
        stage("initialize") {
            def name = params.ASSEMBLY
            if (params.CONFIG_PATH) {
                name = params.CONFIG_PATH
            }
            currentBuild.displayName += " ${params.BUILD_VERSION} - ${name}"
            if (params.RELEASE_ENVIRONMENT) {
                currentBuild.displayName += " ${params.RELEASE_ENVIRONMENT}"
            }
            if (params.DRY_RUN) {
                currentBuild.displayName = "[DRY RUN] " + currentBuild.displayName
            }
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

                if (params.DRY_RUN) {
                    cmd << "--dry-run"
                }
                cmd += [
                    "konflux-release",
                    "--group", "openshift-${params.BUILD_VERSION}",
                    "--assembly", params.ASSEMBLY,
                    "--env", params.RELEASE_ENVIRONMENT,
                    "--config", params.CONFIG_PATH,
                ]
                if (params.SHIPMENT_REPO_URL) {
                    cmd << "--shipment-path=${params.SHIPMENT_REPO_URL}"
                }
                if (params.FORCE) {
                    cmd << "--force"
                }
                withCredentials([
                    file(credentialsId: 'openshift-bot-ocp-konflux-service-account', variable: 'KONFLUX_SA_KUBECONFIG'),
                    string(credentialsId: 'sid-gitlab-access-token', variable: 'GITLAB_TOKEN'),
                    file(credentialsId: 'konflux-gcp-app-creds-prod', variable: 'GOOGLE_APPLICATION_CREDENTIALS'),
                    string(credentialsId: 'konflux-art-images-username', variable: 'KONFLUX_ART_IMAGES_USERNAME'),
                    string(credentialsId: 'konflux-art-images-password', variable: 'KONFLUX_ART_IMAGES_PASSWORD'),
                ]) {
                    echo "Will run ${cmd}"
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
