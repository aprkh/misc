/* Implementation of a Ternary Search Trie with support for
insert, delete, and retrieval. Assumes non-negative value -
outputs -1 for queries not stored in data structure. */

#include <stdio.h>
#include <stdlib.h>

// node class for TST
typedef struct node
{
    char *c;
    int *val;
    struct node *left;
    struct node *mid;
    struct node *right;
} node;

// TST
typedef struct TST
{
    node *root;
} TST;

// functions for operating on TST
TST *newTree(void);
TST *put(TST *t, char *key, int val);
node *putRecursive(node *n, char *key, int val, int index);
int get(TST *t, char *key);
int getRecursive(node *n, char *key, int index);
TST *del(TST *t, char *key);
node *delRecursive(node *n, char *key, int index);
TST *delTree(TST *t);
void delNode(node *n);


int main(void)
{
    TST *t;
    t = newTree();
    if (t == NULL) {
        printf("Error: tree not successfully created in main!\n");
        return 1;
    }

    int R = 63;
    char *alph = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'abcdefghijklmnopqrstuvwxyz";

    // create nTrials new strings, associate with random non-negative value < Lim
    int nTrials = 10;
    int lim = 100;

    int trueVal;
    char *s[nTrials];
    for (int i = 0; i < nTrials; i++) {
        trueVal = rand() % lim;
        int len = rand() % 20;
        printf("The true value is: %i\n", trueVal);

        // create random string
        s[i] = malloc((len+1) * sizeof(char));
        if (s[i] == NULL) {
            printf("Error creating string!\n");
            return 1;
        }
        for (int j = 0; j < len; j++) {
            int u = rand() % R;
            s[i][j] = alph[u];
        }
        s[i][len] = '\0';

        // insert into TST
        put(t, s[i], trueVal);

        // get from TST
        int gotVal = get(t, s[i]);

        // print result
        printf("String: %s, Got value: %i, True value: %i\n", s[i], gotVal, trueVal);
        printf("----------------------------------------------\n");
    }

    for (int i = 1; i < nTrials; i++) {
        t = del(t, s[i]);
    }

    for (int i = 0; i < nTrials; i++) {
        int gotVal = get(t, s[i]);
        printf("String: %s, Got value: %i\n", s[i], gotVal);
    }

    char *missingFirst = "ello world";
    char *hello = "hello world";

    put(t, missingFirst, 123);
    int gotVal = get(t, &hello[1]);

    printf("String: %s, got value: %i (should be 123)\n", missingFirst, gotVal);

    char *empty = "";
    put(t, empty, 456);
    gotVal = get(t, empty);

    printf("Empty string, got value: %i (should be 456)\n", gotVal);
    t = del(t, "");
    gotVal = get(t, "");
    printf("Empty string after deleting, got value: %i (should be -1)\n", gotVal);
    for (int i = 0; i < nTrials; i++) {
        free(s[i]);
    }

    put(t, "HAZELLE", 123);
    printf("Value of HAZELLE (should be 123): %i\n", get(t, "HAZELLE"));

    t = delTree(t);
}


TST *newTree(void)
{
    TST *t = malloc(sizeof(TST));
    if (t == NULL) {
        printf("Error in function newTree:\n");
        printf("Error: failed to create tree!\n");
        exit(1);
    }
    t->root = NULL;
    return t;
}


TST *put(TST *t, char *key, int val)
{
    int index = 0;
    if (t->root == NULL) {
        t->root = malloc(sizeof(node));
        if (t->root == NULL) {
            printf("Error in function put:\n");
            printf("Error: failed to create node!\n");
            exit(1);
        }
        t->root->c = NULL;
        t->root->val = NULL;
        t->root->left = NULL;
        t->root->mid = NULL;
        t->root->right = NULL;
    }
    if (key[0] == '\0') {
        if (t->root->val == NULL) {
            t->root->val = malloc(sizeof(int));
        }
        *(t->root->val) = val;
    } else {
        t->root->mid = putRecursive(t->root->mid, key, val, index);
    }
    return t;
}


node *putRecursive(node *n, char *key, int val, int index)
{
    if (n == NULL) {
        n = malloc(sizeof(node));
        if (n == NULL) {
            printf("Error in function putRecursive: \n");
            printf("Error: failed to create node!\n");
            exit(1);
        }
        n->c = malloc(sizeof(char));
        if (n->c == NULL) {
            printf("Error in function putRecursive: \n");
            printf("Error: failed to allocate memory!\n");
            exit(1);
        }
        n->val = NULL;
        n->mid = NULL;
        n->left = NULL;
        n->right = NULL;
        *(n->c) = key[index];
    }
    if (key[index] < *(n->c)) {
        node *newNode;
        newNode = putRecursive(n->left, key, val, index);
        n->left = newNode;
    } else if (key[index] > *(n->c)) {
        node *newNode;
        newNode = putRecursive(n->right, key, val, index);
        n->right = newNode;
    } else if (key[index+1] != '\0') {
        node *newNode;
        newNode = putRecursive(n->mid, key, val, index+1);
        n->mid = newNode;
    } else {
        if (n->val == NULL) {
            n->val = malloc(sizeof(int));
            if (n->val == NULL) {
                printf("Error in function putRecursive:\n");
                printf("Error: failed to allocate memory for integer!\n");
                exit(1);
            }
        }
        *(n->val) = val;
    }
    return n;
}


int get(TST *t, char *key)
{
    if (t->root == NULL) {
        return -1;
    }
    // handle case of empty string
    if (key[0] == '\0') {
        if (t->root->val == NULL) {
            return -1;
        } else {
            return *(t->root->val);
        }
    }
    int index = 0;
    return getRecursive(t->root->mid, key, index);
}

int getRecursive(node *n, char *key, int index)
{
    if (n == NULL) {
        return -1;
    }
    if (key[index] < *(n->c)) {
        return getRecursive(n->left, key, index);
    } else if (key[index] > *(n->c)) {
        return getRecursive(n->right, key, index);
    } else if (key[index+1] != '\0') {
        return getRecursive(n->mid, key, index+1);
    } else {
        int out;
        // note that we need to check for short prefixes
        if (n->val == NULL) {
            out = -1;
        } else {
            out = *(n->val);
        }
        return out;
    }
}

/* Delete key from tree */
TST *del(TST *t, char *key)
{
    // handle passage of empty string
    if (key[0] == '\0') {
        if (t->root != NULL && t->root->val != NULL) {
            free(t->root->val);
            t->root->val = NULL;
        }
        return t;
    }
    int index = 0;
    if (t->root->mid == NULL) {
        return t;
    }
    t->root->mid = delRecursive(t->root->mid, key, index);
    return t;
}

node *delRecursive(node *n, char *key, int index)
{
    if (n == NULL) {
        return NULL;
    }
    if (key[index] < *(n->c)) {
        n->left = delRecursive(n->left, key, index);
    } else if (key[index] > *(n->c)) {
        n->right = delRecursive(n->right, key, index);
    } else if (key[index+1] != '\0') {
        n->mid = delRecursive(n->mid, key, index+1);
    } else {
        free(n->val);
        n->val = NULL;
    }


    /* if there are no more nodes down the middle path, check if we can delete this node.
       we can delete the middle node if there are no left or right paths as well as the
       middle path. */

    if (n->val == NULL && n->mid == NULL) {
        if (n->left == NULL && n->right == NULL) {
            free(n->c);
            free(n);
            return NULL;
        } else if (n->left == NULL) {
            node *rightNode = n->right;
            free(n->c);
            free(n);
            return rightNode;
        } else if (n->right == NULL) {
            node *leftNode = n->left;
            free(n->c);
            free(n);
            return leftNode;
        }
    }

    return n;
}

/* Deletes entire tree */
TST *delTree(TST *t)
{
    node *root = t->root;
    delNode(root);
    root = NULL;
    free(t);
    t = NULL;
    return t;
}

void delNode(node *n)
{
    if (n == NULL) {
        return;
    }

    if (n->left != NULL) delNode(n->left);
    if (n->mid != NULL) delNode(n->mid);
    if (n->right != NULL) delNode(n->right);

    free(n->c);
    free(n->val);
    free(n);
}
