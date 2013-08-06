public enum EnumTest{
    A,B;
    public static void main(String[] args){
        EnumTest[] xs = new EnumTest[]{A,B};
        for (EnumTest x : xs){
            switch (x){
                case A:
                    System.out.println("A");
                    break;
                case B:
                    System.out.println("B");
                    break;
            }
        }
    }
}

