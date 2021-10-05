# Qanary Quality Assurance (beta)

This project provides a helper for evaluating your Qanary-based Question Answering system. In general, it is providing you a framework for controlling the quality of a QA system. The script can be fully customized to meet the requirements of your QA system.

## Motivation: End-to-end Microbenchmarking

Typical QA systems depend on several components. We need to control the quality of all components, s.t., we know:

1. if the expected functionality is actually achieved (not just claimed),
2. if changes of the QA system are improving the quality of the system (and not decreasing the quality), and
3. what needs to be improved next.

Hence, we need automatic end-to-end tests while also evaluating each process step. This is called *end-to-end micro-benchmarking* Fortunately, Qanary is already providing the interfaces to conveniently control the quality of a QA system.

The quality is evaluated using SPARQL queries to the Qanary triplestore as it contains all relevant information of the QA process for a given question. Hence, we will define questions that will be executed on your QA system and check thereafter if the expected information is contained in the Qanary triplestore.

## Execute the Microbenchmarking Script

The benchmarking tool is started while providing a directory that contains all configuration files (executed using a Python 3 interpreter):

```bash
python evaluate-qanary-system.py --directory=<DIRECTORYNAME>
```

Example:

```bash
python evaluate-qanary-system.py --directory=superhero-real-names
```

The script will create a *logfile*, a *JSON file* containing all test results in JSON format, and an *XLSX file* containing a tabular representation of the test results including a predefined chart showing visually the measured quality of your QA system.

## Prepare the Test Environment

### Clone the directory

```bash
git clone git@github.com:anbo-de/Qanary-quality-assurance.git
```

or

```bash
git clone https://github.com/anbo-de/Qanary-quality-assurance.git
```

The test script is useing Python 3. Install Python dependencies using pip:

```bash
pip install -r requirements.txt 
```

### Prepare Test Data

#### Step 1. Create a directory that will contain all the test data

#### Step 2. Create a file `qanary-test-definition.json`

The configuration of the tests is defined in the file `qanary-test-definition.json`. The structure of the file is as follows:

```json
{
    "qanary": {
        "system_url": "...",
        "componentlist": [ ... ],
        "qanary_triplestore_endpoint": "...",
        "qanary_triplestore_database": "...",
        "qanary_triplestore_username": "...",
        "qanary_triplestore_password": "..."
    },
    "validation-sparql-templates": [ ... ],
    "custom-validation": "...",
    "tests": [ ... ]
}
```

##### Section `qanary`

The `qanary` section configures the connection data to the Qanary system (see [example](superhero-real-names/qanary-test-definition.json)).

##### Section `validation-sparql-templates`

Here a list of filenames defined referring to files where each is containing one SPARQL ASK query template. An ASK query responds with `True` or `False`. Hence, this is perfectly suited for validating if the Qanary triplestore contains the expected information. All ASK queries templates in the list will be processed for each (later defined) question.

One important issue is the use of a placeholder which is typically required to customize the query for each question. Any string can be a placeholder, therefore, choose a unique string to prevent problems during the replacing of the placeholders. A default replacement key is defined: `<GRAPHID>`. It is used to inject the name of the current graph in your query template.

See the section [Step 3. Create ASK query template files](#step-3-create-ask-query-template-files) for ASK queries.

##### Section `custom-validation`

Typically at the last step of the quality control process, one would like to check if it is possible to actually retrieve the answer from the target data (i.e., the data that should contain the answer to the given question). For example, you might use your computed answer SPARQL query to retrieve data from DBpedia. This step cannot be generalized. Therefore, a custom test file is defined here. The file contains the test function named `validate` that is defined as follows:

```python
def validate(test, logger, conf_qanary, connection, graphid):
```

Hence, one can work with the `test` object (see above), a `connection` to the Qanary triplestore ([Stardog connection](https://pystardog.readthedocs.io/en/latest/source/stardog.html#module-stardog.connection)), and the `graphid` is referring to the graph containing the current process data of the question defined in the test (see below). The `logger` is writing to the standard file log (see above). The dictionary `conf_qanary` is containing the data of the section `qanary` (see above). You can implement anything you want in this method. However, the method *needs* to return `True` or `False`.

The method `validate` needs to be available. If you do not need this custom implementation, then define the method as follows:

```python
def validate(test, logger, conf_qanary, connection, graphid):
    return False
```

An example is available [here](superhero-real-names/execute-on-dbpedia.py).

##### Section `tests`

This section contains an array of test objects. Each object has the following structure:

```json
    {
            "question": "TEXT",
            "replacements": {
                "KEY0": "VALUE0",
                "KEY1": "VALUE1"
            }
    }
```

The property `question` contains the textual question. The property `replacements` is an object defining *search* (placeholder) and *replace* (new value) structures. They are applied to all ASK SPARQL queries individually depending on the currently processed question. Hence, here an ASK query *templates* are transformed into an executable ASK query. Examples see [here](superhero-real-names/qanary-test-definition.json#L19).

#### Step 3. Create ASK query template files

For each test template defined in the section `validation-sparql-templates` a file needs to be created. The file need to contain a ASK SPARQL query (i.e., each query need to return `True` or `False`).

For details on ASK queries see https://www.futurelearn.com/info/courses/linked-data/0/steps/16094 or https://codyburleson.com/blog/sparql-examples-ask. For examples of a real test configuration see [here](superhero-real-names/0_was-any-instance-identified.sparql), [here](superhero-real-names/1_was-the-expected-instace-recognized.sparql) and [here](superhero-real-names/2_was-a-sparql-query-computed-similar-as-expected.sparql).

## Evaluation

After the execution of the test script a new directory `output` is created (if not existing before). It will contain the output files:

* The *logfile* contains a log of the actions during the tests.
* The *JSON file* contain the complete test results in JSON format.
* The *XLXS file* contains a tabular representation of the test results and an automatically created chart showing the quality visually. Example:  
  ![table](./superhero-real-names/example-output/table.png)  
  ![chart](./superhero-real-names/example-output/chart.png)

Every file name contain the timestamp (datetime when the test was started). If the test is executed several times, then the files are not overwritten.

See the stored [exemplary tests](superhero-real-names/example-output/) for the output structure.

## Complete Example

See the folder [superhero-real-names](superhero-real-names/) for a complete example.

## Limitations

The script is currently designed for textual questions only. Feel free to modify the script to meet your requirements.

The script is evaluating one scenario only (e.g., one type of questions). Typucally, in a project there will be many scenarions. In this case just define several directories containing particular definitions for an additional scenario.
