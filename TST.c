/* C implementation of a Ternary Search Trie with support for
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
    t = malloc(sizeof(TST));

    char *s;
    s = "Hello";

    t = put(t, s, 100);

    int a = get(t, s);

    printf("value of %s: %i\n", s, a);

    char *ss = "goodbye";
    a = get(t, ss);
    printf("value of %s: %i\n", ss, a);

    t = put(t, s, 500);
    a = get(t, s);
    printf("value of %s: %i\n", s, a);

    t = del(t, s);
    a = get(t, s);
    printf("value of %s: %i\n", s, a);

    t = delTree(t);
}


TST *put(TST *t, char *key, int val)
{
    if (key[0] == '\0') return t;
    int index = 0;
    if (t->root == NULL) {
        t->root = malloc(sizeof(node));
        t->root->c = NULL;
        t->root->val = NULL;
    }
    t->root->mid = putRecursive(t->root->mid, key, val, index);
    return t;
}


node *putRecursive(node *n, char *key, int val, int index)
{
    if (n == NULL) {
        n = malloc(sizeof(node));
        n->c = malloc(sizeof(char));
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
        n->val = malloc(sizeof(int));
        *(n->val) = val;
    }
    return n;
}


int get(TST *t, char *key)
{
    if (t->root == NULL) {
        printf("Error! Ternary Search Trie is empty!\n");
        exit(1);
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
        int out = *(n->val);
        return out;
    }
}

/* Delete key from tree */
TST *del(TST *t, char *key)
{
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
        n->val = NULL;
    }

    /* if there are no more nodes down the middle path, check if we can delete this node.
       we can delete the middle node if there are no left or right paths as well as the
       middle path. */
    if (n->val == NULL && n->mid == NULL) {
        if (n->left == NULL && n->right == NULL) {
            return NULL;
        } else if (n->left == NULL) {
            return n->right;
        } else if (n->right == NULL) {
            return n->left;
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
    delNode(n->left);
    delNode(n->mid);
    delNode(n->right);

    free(n->c);
    free(n->val);
    free(n);
}
