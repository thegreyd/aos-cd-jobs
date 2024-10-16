node() {
    wrap([$class: "BuildUser"]) {
        // gomod created files have filemode 444. It will lead to a permission denied error in the next build.
        sh "chmod u+w -R ."
        checkout scm
        def buildlib = load("pipeline-scripts/buildlib.groovy")
        def commonlib = buildlib.commonlib

        commonlib.describeJob("build-microshift", """
            <h2>Rebase and build MicroShift for an assembly.</h2>
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
                            description: "The name of an assembly to rebase & build for. e.g. 4.9.1",
                            defaultValue: "test",
                            trim: true
                        ),
                        booleanParam(
                            name: "FORCE_REBUILD",
                            description: "(For named assemblies) Rebuild even if a build already exists",
                            defaultValue: false
                        ),
                        string(
                            name: 'RELEASE_PAYLOADS',
                            description: '(Optional) List of release payloads to rebase against; can be nightly names or full pullspecs',
                            defaultValue: "",
                            trim: true,
                        ),
                        booleanParam(
                            name: "NO_REBASE",
                            description: "(For testing only) Do not rebase microshift code; build the current source we have in the upstream repo",
                            defaultValue: false
                        ),
                        booleanParam(
                            name: "NO_ADVISORY_PREP",
                            description: "(For testing only) Do not prepare microshift advisory for named assemblies",
                            defaultValue: false
                        ),
                        string(
                            name: 'DOOZER_DATA_PATH',
                            description: 'ocp-build-data fork to use (e.g. assembly definition in your own fork)',
                            defaultValue: "https://github.com/openshift-eng/ocp-build-data",
                            trim: true,
                        ),
                        booleanParam(
                            name: 'IGNORE_LOCKS',
                            description: 'Do not wait for other builds in this version to complete (use only if you know they will not conflict)',
                            defaultValue: false
                        ),
                        booleanParam(
                            name: "DRY_RUN",
                            description: "Take no action, just echo what the job would have done.",
                            defaultValue: false
                        ),
                        commonlib.mockParam(),
                    ]
                ],
            ]
        )

        commonlib.checkMock()
        stage("initialize") {
            currentBuild.displayName += " $params.BUILD_VERSION - $params.ASSEMBLY"
            if (params.DRY_RUN) {
                currentBuild.displayName += "[DRY RUN] " + currentBuild.displayName
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
                    "build-microshift",
                    "--data-path", params.DOOZER_DATA_PATH,
                    "-g", "openshift-$params.BUILD_VERSION",
                    "--assembly", params.ASSEMBLY,
                ]
                if (params.RELEASE_PAYLOADS) {
                    for (nightly in commonlib.parseList(params.RELEASE_PAYLOADS)) {
                        cmd << "--payload" << nightly.trim()
                    }
                }
                if (params.FORCE_REBUILD) {
                    cmd << "--force"
                }
                if (params.NO_REBASE) {
                    cmd << "--no-rebase"
                }
                if (params.NO_ADVISORY_PREP) {
                    cmd << "--no-advisory-prep"
                }
                withCredentials([
                    string(credentialsId: 'art-bot-slack-token', variable: 'SLACK_BOT_TOKEN'),
                    string(credentialsId: 'jboss-jira-token', variable: 'JIRA_TOKEN'),
                    string(credentialsId: 'openshift-bot-token', variable: 'GITHUB_TOKEN'),
                    string(credentialsId: 'jenkins-service-account', variable: 'JENKINS_SERVICE_ACCOUNT'),
                    string(credentialsId: 'jenkins-service-account-token', variable: 'JENKINS_SERVICE_ACCOUNT_TOKEN'),
                    file(credentialsId: 'konflux-gcp-app-creds-prod', variable: 'GOOGLE_APPLICATION_CREDENTIALS'),
                    file(credentialsId: 'openshift-bot-konflux-service-account', variable: 'KONFLUX_SA_KUBECONFIG'),
                ]) {
                    echo "Will run ${cmd}"
                    buildlib.withAppCiAsArtPublish() {
                        if (params.IGNORE_LOCKS) {
                            commonlib.shell(script: cmd.join(' '))
                        } else {
                            lock("build-microshift-lock-${params.BUILD_VERSION}") { commonlib.shell(script: cmd.join(' ')) }
                        }
                    }
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
