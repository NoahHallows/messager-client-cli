#include <Python.h>
#include <stdio.h>

int main() {
    Py_Initialize();

    // Add current directory to Python path
    PyRun_SimpleString("import sys; sys.path.append('.')");

    // Import client_backend
    PyObject *pName = PyUnicode_FromString("client_backend");
    PyObject *pModule = PyImport_Import(pName);
    Py_DECREF(pName);

    if (pModule) {
        // Get ChatClient class
        PyObject *pClass = PyObject_GetAttrString(pModule, "ChatClient");

        if (pClass && PyCallable_Check(pClass)) {
            PyObject *pClient = PyObject_CallObject(pClass, NULL);  // Create ChatClient instance

            if (pClient) {
                // Call connect()
                PyObject *pResult = PyObject_CallMethod(pClient, "connect", NULL);
                if (pResult && PyObject_IsTrue(pResult)) {
                    printf("Connected to server!\n");

                    // Call login(username, password)
                    PyObject *loginResult = PyObject_CallMethod(pClient, "login", "ss", "Noah", "amicia");
                    if (loginResult) {
                        PyObject *success = PyTuple_GetItem(loginResult, 0);
                        PyObject *message = PyTuple_GetItem(loginResult, 1);
                        printf("Login result: %s\n", PyUnicode_AsUTF8(message));
                        Py_DECREF(loginResult);
                    }

                    // Send message
                    PyObject *sendResult = PyObject_CallMethod(pClient, "send_message", "s", "Hello from C UI!");
                    if (sendResult && PyObject_IsTrue(sendResult)) {
                        printf("Message sent.\n");
                    }

                    Py_XDECREF(sendResult);
                }

                Py_XDECREF(pResult);
                Py_DECREF(pClient);
            }
        }

        Py_XDECREF(pClass);
        Py_DECREF(pModule);
    } else {
        PyErr_Print();
        fprintf(stderr, "Failed to load client_backend.py\n");
    }

    Py_Finalize();
    return 0;
}

