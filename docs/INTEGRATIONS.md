Integrations
------------

GitHub Actions (PR fastpath)
----------------------------

See `ci/pr-fastpath.yml`. It:
- Installs Python and Go
- Builds artifacts for the multi-entry Go sample with strict reproducibility
- Verifies golden files
- Uploads SARIF for PR annotations

GitHub Actions (Release)
------------------------

See `ci/release.yml`. It:
- Builds and publishes the Python wheel to PyPI (requires `PYPI_USERNAME` and `PYPI_PASSWORD` repo secrets)
- Builds and pushes a Docker image to GHCR using the repo’s GITHUB_TOKEN

GitLab CI (example)
-------------------

```yaml
stages: [fastpath]

fastpath:
  image: python:3.12
  stage: fastpath
  before_script:
    - pip install noisecutter
    - curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | bash -s -- -b /usr/local/bin v1.16.0
  script:
    - cd examples/go-multi-entry
    - make all_artifacts
    - make verify-golden
  artifacts:
    when: always
    paths:
      - examples/go-multi-entry/report.*.sarif
```

Jenkins (example)
-----------------

Declarative pipeline snippet:

```groovy
pipeline {
  agent any
  stages {
    stage('Setup') {
      steps {
        sh 'pip install noisecutter'
        sh 'curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | bash -s -- -b ./bin v1.16.0'
        sh 'export PATH=$PWD/bin:$PATH'
      }
    }
    stage('Fastpath') {
      steps {
        dir('examples/go-multi-entry') {
          sh 'make all_artifacts'
          sh 'make verify-golden'
        }
      }
    }
    stage('Publish SARIF') {
      steps {
        archiveArtifacts artifacts: 'examples/go-multi-entry/report.*.sarif', fingerprint: true
      }
    }
  }
}
```


