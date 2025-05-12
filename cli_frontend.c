#include <Python.h>
#include <stdio.h>
#include <gtk/gtk.h>

static void login_btn_func(GtkButton *login_btn) {
  const char *s;

  s = gtk_button_get_label(login_btn);
  if (g_strcmp0(s, "Login") == 0) {
    gtk_button_set_label(login_btn, "Loged in!!!");
  } else {
    gtk_button_set_label(login_btn, "Login");
  }
}



static void
app_activate (GApplication *app) {
  GtkWidget *win;
  GtkWidget *box;
  GtkWidget *btn1;
  GtkWidget *lab;
  win = gtk_application_window_new(GTK_APPLICATION(app));
  gtk_window_set_title(GTK_WINDOW(win), "Quackmessage");
  gtk_window_set_default_size(GTK_WINDOW(win), 400, 300);
  
  box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 5);
  gtk_box_set_homogeneous(GTK_BOX(box), TRUE);
  gtk_window_set_child(GTK_WINDOW(win), box);


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

